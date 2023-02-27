'''
De-identification code for Italian Clinical Text

'''

import pandas as pd

import dateutil.parser
# from typing import Match
from functools import reduce
import json
import os

import sparknlp
import sparknlp_jsl
from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from sparknlp.base import *
from sparknlp.util import *
# nota: verificare se servono tutti questi import per jhonsnowlab o bastano quelli con #i

import re

tc = '■' # temporary character for replacement

def empty_db():
  return pd.DataFrame(columns=['start','end','entity_type','text'])

def merge_overlaps(df):
  # this functions checks spans order by start and end and in case of overlaps only considers first appearing span
  # il primo reset index è per evitare indici duplicati ma mantenere l'ordine di preferenza (nella lista i db prima verranno messi prima come priorità), il secondo è per resettare dopo il sort
  dbtot = df.reset_index(drop=True).sort_values(by=['start','end']).reset_index(drop=True)
  dbase = dbtot[dbtot.index==0].copy()
  db2add = dbtot[dbtot.index!=0]
  for i,row in db2add.iterrows():
    if row['start']>dbase['end'].max():
      dbase = pd.concat((dbase,db2add[db2add.index==i]))
  return dbase.reset_index(drop=True)

class anonymizer:
  def __init__(self, configfile):
    self.supported_ents = ['telephone','zipcode','email','fiscal_code','person','organization','address','date','age']
    self.supported_mask_modes = ['tag','tag_l','anon','anon_l']
    self.models = {k:'' for k in self.supported_ents}
    self.mode = 'tag'
    self.sc = '*'
    self.date_level = 'hide'
    self.find_func_dict = {
      "person": self.FindPerson,
      "organization": self.FindOrganization,
      "telephone": self.FindTelephone,
      "date": self.FindDate,
      "age": self.FindAge,
      "email": self.FindEmail,
      "zipcode": self.FindZipCode,
      "address": self.FindAddress,
      'fiscal_code': self.FindFiscalCode
    }

    self.load(configfile)

  def load(self, configfile): # takes json file as argument
    # parse configuration file
    with open(configfile) as cin:
      cfg = json.load(cin)
    self.load_dict(cfg)

  def load_dict(self, cfg): # takes dict as argument
    print('new config:', cfg)
    prev_models = set(self.models.values()) # get currently loaded models
    print('prev_models:', prev_models)
    # parse dictionary. keeps default or current values if a parameter is not passed
    if 'models' not in cfg: cfg['models'] = {}
    for ent in self.supported_ents:
      if ent in cfg['models']:
        self.models[ent] = cfg['models'][ent]
    if 'mask' in cfg:
      if 'mode' in cfg['mask']:
        self.mode = cfg['mask']['mode']
      if 'special_character' in cfg['mask']:
        self.sc = cfg['mask']['special_character'][0] # take only first character if a string is passed
      if 'date_level' in cfg['mask']:
        self.date_level = cfg['mask']['date_level']
    print(self.models)
    current_models = set(self.models.values())
    self.tracker = pd.DataFrame(self.models.items(),columns=['entity_type','model'])
    self.tracker['status'] = False # status to avoid rerunning the same ner models multiple times
    self.dbs = empty_db() # results dataframe

    # initialize needed models
    print(f'{"DOWNLOADING AND INITIALIZING MODELS ":-<80}')
    for model in current_models-prev_models: # using set difference to add missing models
      if model=='stanza':
        import stanza # to install with pip
        stanza.download("it")
        self.m_stanza = stanza.Pipeline(lang="it", processors='tokenize, ner')
        #todo: needs to check if stanza is trying to be used on other entities which are not supported
      elif model=='spacy':
       import spacy #to install with pip
       # Install 'python -m spacy download it_core_news_lg'
       self.m_spacy = spacy.load("it_core_news_lg")
      elif model=='regex':
        # All the regex refers to Italian Style for telephone, zip code, etc ---
        pass # nothing to load
      elif model=='john':
        from sparknlp.pretrained import PretrainedPipeline #i
        from pyspark.ml import Pipeline, PipelineModel
        from pyspark.sql import SparkSession
        from sparknlp.pretrained import ResourceDownloader
        from pyspark.sql import functions as F
        # nota: verificare se servono tutti questi import per jhonsnowlab o bastano quelli con #i

        with open('spark_jsl.json') as f:
          license_keys = json.load(f)

        # Defining license key-value pairs as local variables
        locals().update(license_keys)
        os.environ.update(license_keys)

        params = {"spark.driver.memory": "16G",
                  "spark.kryoserializer.buffer.max": "2000M",
                  "spark.driver.maxResultSize": "2000M"}

        spark = sparknlp_jsl.start(secret=os.environ.get('SECRET'), params=params)
        self.m_john = PretrainedPipeline("clinical_deidentification", "it", "clinical/models")
      elif model!='':
        print(f'{model} is not a supported model. Please check the documentation for the list of supported models for each field')
    for model in prev_models-current_models: # using set difference to release memory for no more needed models
      pass #TODO. freeing memory instructions is hard to find in the documentation, i only found about spacy
    return

  # main function
  def deIdentificationIta(
      self,
      inputText,
      merge=False
    ):
    #print(f'{"ANONYMIZING GIVEN TEXT ":-<80}')
    self.dbs = empty_db() # resets previously found entities
    for entity_type in self.supported_ents:
      self.find_func_dict[entity_type](inputText, concat=True)

    self.Find_with_John(inputText, concat=True)
    self.Find_with_Spacy(inputText, concat=True)
    self.Find_with_Stanza(inputText, concat=True)
    # decide if the returned dataframes can be useful. careful if using same ner for multiple ents, some dbs have all the ents and others are empty to avoid rerunning
    # _ = self.FindTelephone(inputText, concat=True)
    # _ = self.FindZipCode(inputText, concat=True)
    # _ = self.FindEmail(inputText, concat=True)
    # _ = self.FindPerson(inputText, concat=True)
    # _ = self.FindOrganization(inputText, concat=True)
    # _ = self.FindAddress(inputText, concat=True)
    # _ = self.FindDate(inputText, concat=True)
    # _ = self.FindFiscalCode(inputText, concat=True)
    # _ = self.FindAge(inputText, concat=True)
    print(self.dbs)
    self.tracker['status'] = False # resets found entities for future reruns on different text
    outText = self.mask_data(inputText)
    if merge: # merges found spans before returning, aligning dbs with anonymized text
      return {'text': outText, 'match_dataframe': merge_overlaps(self.dbs)}
    else: # returns all found spans
      return {'text': outText, 'match_dataframe': self.dbs}

  # masker function. replace sensible text with tag name (optional) and special character
  def mask_data(self, inputText, dbs=None, mode=None, date_level=None, sc=None):
    # use class variables as default but lets the user call just mask_data if no Finds are needed
    if dbs is None: dbs=self.dbs
    if mode is None: mode=self.mode
    if date_level is None: date_level=self.date_level
    if sc is None: sc=self.sc

    if mode not in self.supported_mask_modes:
      print(f'WARNING: Unsupported masking mode selected. Choose one from {self.supported_mask_modes}.')
      return inputText
    if len(dbs)==0:
      return inputText

    # makes a unique span dataframe taking only first span in case of overlaps
    dbase = merge_overlaps(dbs)

    outText = ''
    for i in range(len(dbase)):
      if i==0:
        p_end = 0 # for first iteration get string start
      else:
        p_end = dbase.loc[i-1]['end'] # end of previous span
      row = dbase.loc[i]
      field_len = row['end']-row['start'] # length of text to anonymize
      outText += inputText[p_end:row['start']] # concats normal text between spans

      if row['entity_type']=='DATA' and date_level!='hide': # additional types of anonymization for dates
        data_to_hide = row['text']
        data_finder = dateutil.parser.parse(data_to_hide, dayfirst=True)
        if date_level == 'year':
          outText += f'{data_finder.year}'
        elif date_level == 'month':
          outText += f'{data_finder.month}-{data_finder.year}'
        else: # this should never occur cause of the check in FindDate
          outText += data_to_hide

      else: # non-date entity_types, or dates with "hide" level behaving as other entities
        if mode=='anon_l' or mode=='anon':
          outText += tc*(field_len)
        elif mode=='tag_l' or mode=='tag':
          outText += f'{"<"+row["entity_type"]+">":{tc}<{field_len}}' # also puts angular brackets around entity_type
          # !!! NB: if entity_type string is longer than text string, overall text length will increase
        #todo: elif self.mode=='random'
    outText += inputText[dbase.iloc[-1]['end']:] # concat last piece of text after last span

    if mode=='anon':
      outText = re.sub(f'{tc}+', tc*3, outText) # you can set how long the fixed character replacement will be here
    if mode=='tag':
      outText = outText.replace(tc,'')
    outText = outText.replace(tc,sc)
    return outText

  # entity finder functions
  # concat is false by default meaning results won't be appended to object dbs, letting you call individual functions when needed
  def FindTelephone(self, inputText, concat=False):
    if self.models['telephone']=='regex':
      matches = re.finditer('(?:(\(?(?:\+|00)\(?\d{2,3}\)?)[\s\-\.\\\\]?)?((?:3\d{2}[\s\-\.\/\\\\]?\d{7})|(?:0\d[\s\-\.\/\\\\]?\d{8})|(?:0\d{2}[\s\-\.\/\\\\]?\d{5,7})|(?:0\d{3}[\s\-\.\/\\\\]?\d{5,6}))', inputText)
      span_list = [(match.span()[0], match.span()[1], match.group(), 'regex') for match in matches]
      db = pd.DataFrame(span_list, columns=['start','end','text', 'model'])
      db['entity_type'] = 'TELEFONO'
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type']=='telephone','status']=True
      return db
    # elif self.models['telephone']=='john':
    #   return self.Find_with_John(inputText, concat)
    elif self.models['telephone']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for telephone anonymization')
    #   return empty_db()

  def FindZipCode(self, inputText, concat=False):
    if self.models['zipcode']=='regex':
      matches = re.finditer('\D([0-9]{5})\D', inputText)
      span_list = [(match.span(1)[0], match.span(1)[1], match.group(1), 'regex') for match in matches] # (1) because it's first capturing group to avoid surrounding non-digits captured
      db = pd.DataFrame(span_list, columns=['start','end','text', 'model'])
      db['entity_type'] = 'CAP'
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type']=='zipcode','status']=True
      return db
    # elif self.models['zipcode']=='john':
    #   return self.Find_with_John(inputText, concat)
    elif self.models['zipcode']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for zipcode anonymization')
    #   return empty_db()

  def FindEmail(self, inputText, concat=False):
    if self.models['email']=='regex':
      matches = re.finditer('[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}', inputText)
      span_list = [(match.span()[0], match.span()[1], match.group(), 'regex') for match in matches]
      db = pd.DataFrame(span_list, columns=['start','end','text', 'model'])
      db['entity_type'] = 'E-MAIL'
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type']=='email','status']=True
      return db
    # elif self.models['email']=='john':
    #   return self.Find_with_John(inputText, concat)
    elif self.models['email']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for e-mail anonymization')
    #   return empty_db()

  def FindFiscalCode(self, inputText, concat=False):
    if self.models['fiscal_code']=='regex':
      matches = re.finditer('[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]', inputText)
      span_list = [(match.span()[0], match.span()[1], match.group(), 'regex') for match in matches]
      db = pd.DataFrame(span_list, columns=['start','end','text', 'model'])
      db['entity_type'] = 'CF'
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type']=='fiscal_code','status']=True
      return db
    # elif self.models['fiscal_code']=='john':
    #   return self.Find_with_John(inputText, concat)
    elif self.models['fiscal_code']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for fiscal code anonymization')
    #   return empty_db()

  def FindPerson(self, inputText, concat=False):
    # if self.models['person']=='stanza':
    #   return self.Find_with_Stanza(inputText, concat)
    # elif self.models['person']=='spacy':
    #   return self.Find_with_Spacy(inputText, concat)
    # elif self.models['person']=='john':
    #   return self.Find_with_John(inputText, concat)
    if self.models['person']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for person anonymization')
    #   return empty_db()

  def FindOrganization(self, inputText, concat=False):
    # if self.models['organization']=='stanza':
    #   return self.Find_with_Stanza(inputText, concat)
    # elif self.models['organization']=='spacy':
    #   return self.Find_with_Spacy(inputText, concat)
    # elif self.models['organization']=='john':
    #   return self.Find_with_John(inputText, concat)
    if self.models['organization']=='':
      return empty_db()

  def FindAddress(self, inputText, concat=False):
    # if self.models['address']=='stanza':
    #   return self.Find_with_Stanza(inputText)
    # elif self.models['address']=='spacy':
    #   return self.Find_with_Spacy(inputText, concat)
    # elif self.models['address']=='john':
    #   return self.Find_with_John(inputText, concat)
    if self.models['address']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for address anonymization')
    #   return empty_db()

  def FindAge(self, inputText, concat=False):
    # if self.models['age']=='john':
    #    return self.Find_with_John(inputText, concat)
    if self.models['age']=='':
      return empty_db()
    if self.models['age'] == 'regex':
      matches = re.finditer(
        r'(?:(?:(\d+)\s*anni)|(?:anni\s*(\d+)))',
        inputText.lower())
      span_list = [(match.span()[0], match.span()[1], match.group(), 'regex') for match in matches]
      db = pd.DataFrame(span_list, columns=['start', 'end', 'text', 'model'])
      db[
        'entity_type'] = 'ETÀ'
      self.tracker.loc[self.tracker['entity_type'] == 'age', 'status'] = True
      if concat: self.dbs = pd.concat((self.dbs, db))
      return db
    else:
      if self.models['age'] != 'john':
       print('WARNING: Unsupported model for age anonymization')
      return empty_db()

  def FindDate(self, inputText, concat=False):
    if self.date_level not in ['hide','year','month']:
      print('WARNING: Unsupported type of date anonymization. It should be hide, year or month.')
      return empty_db()
    if self.models['date']=='regex':
      matches = re.finditer('(?:\d{1,4}[-\\ \/  \.])?(\d{1,2}|(?:gen(?:naio)?|feb(?:braio)?|mar(?:zo)?|apr(?:ile)?|mag(?:gio)|giu(?:gno)?|lug(?:lio)?|ago(?:sto)?|set(?:tembre)?|ott(?:obre)?|nov(?:embre)?|dic(?:embre)?))[-\\ \/  \.]\d{1,4}',inputText.lower())
      span_list = [(match.span()[0], match.span()[1], match.group(), 'regex') for match in matches]
      db = pd.DataFrame(span_list, columns=['start','end','text', 'model'])
      db['entity_type'] = 'DATA' #this is important to check for additional anonym. types for dates. if you change this, should also change the if in mask_data
      self.tracker.loc[self.tracker['entity_type']=='date','status']=True
    # elif self.models['date']=='john':
    #   db = self.Find_with_John(inputText, concat)
    elif self.models['date']=='':
      return empty_db()
    # else:
    #   print('WARNING: Unsupported model for date anonymization')
    #   return empty_db()

    m = db.apply(self.IsValidDate, axis=1)
    db = db[m]
    if concat: self.dbs = pd.concat((self.dbs, db))
    return db

  def IsValidDate(self, df_row):
    dateText = df_row['text']
    tuple_months = ('gennaio', '01'), ('gen', '01'), ('febbraio', '02'), ('feb', '02'), ('marzo', '03'), ('mar', '03'), (
    'aprile', '04'), ('apr', '04'), ('maggio', '05'), ('mag', '05'), ('giugno', '06'), ('giu', '06'), (
                  'luglio', '07'), ('lug', '07'), ('agosto', '08'), ('ago', '08'), ('settembre', '09'), ('set', '09'), (
                  'ottobre', '10'), ('ott', '10'), ('novembre', '11'), ('nov', '11'), ('dicembre', '12'), ('dic', '12')
    if (not (re.search('[a-zA-Z]', dateText)) == None):
      dateText = reduce(lambda a, kv: a.replace(*kv), tuple_months, dateText)  # replaces textual month with numeric equivalent
    try:
      dateutil.parser.parse(dateText, dayfirst=True)
    except dateutil.parser.ParserError: #as e:
      return False
    return True

  # ner functions for multiple entities, to avoid rerunning
  def Find_with_Stanza(self, inputText, concat=False):
    ents = self.tracker[self.tracker['model']=='stanza']
    ents_todo = ents[ents['status']==False]
    if len(ents_todo)>0: # check if there are still entities to find
      doc = self.m_stanza(inputText)
      span_list = [(e.start_char, e.end_char, e.type, e.text, 'stanza') for e in doc.ents]
      db = pd.DataFrame(span_list, columns=['start','end','entity_type','text', 'model'])
      db['entity_type'] = db['entity_type'].replace({'PER':'person','LOC':'address','ORG':'organization'})
      db = db[db['entity_type'].isin(ents_todo['entity_type'])].copy() # keep only entities selected with this model
      db['entity_type'] = db['entity_type'].replace({'person':'PERSONA','address':'INDIRIZZO','organization':'ORGANIZZAZIONE'})
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type'].isin(ents_todo['entity_type']),'status']=True # set detected entities as done
      return db
    else:
      return empty_db() # entities already found by another Find call of the same model

  def Find_with_Spacy(self, inputText, concat=False):
    ents = self.tracker[self.tracker['model']=='spacy']
    ents_todo = ents[ents['status']==False]
    if len(ents_todo)>0: # check if there are still entities to find
      doc = self.m_spacy(inputText)
      span_list = [(e.start_char, e.end_char, e.label_, e.text, 'spacy') for e in doc.ents]
      db = pd.DataFrame(span_list, columns=['start','end','entity_type','text', 'model'])
      db['entity_type'] = db['entity_type'].replace({'PER':'person','LOC':'address','ORG':'organization'})
      db = db[db['entity_type'].isin(ents_todo['entity_type'])].copy() # keep only entities selected with this model
      db['entity_type'] = db['entity_type'].replace({'person':'PERSONA','address':'INDIRIZZO','organization':'ORGANIZZAZIONE'})
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type'].isin(ents_todo['entity_type']),'status']=True # set detected entities as done
      return db
    else:
      return empty_db() # entities already found by another Find call of the same model

  def Find_with_John(self, inputText, concat=False):
    ents = self.tracker[self.tracker['model']=='john']
    ents_todo = ents[ents['status']==False]
    if len(ents_todo)>0: # check if there are still entities to find
      annotations = self.m_john.fullAnnotate(inputText)
      span_list = [(a.begin, a.end + 1 , a.metadata['entity'], a.result, 'john') for a in annotations[0]['ner_chunk']] #!!! probabilmente non ci va questo == SSN
      db = pd.DataFrame(span_list, columns=['start','end','entity_type','text', 'model'])
      db['entity_type'] = db['entity_type'].replace({'DOCTOR':'person','PATIENT':'person', 'CITY':'address','HOSPITAL':'organization' ,'E-MAIL':'email', 'AGE':'age', 'SSN':'fiscal_code', 'ZIP':'zipcode', 'TELEPHONE':'telephone'})
      db = db[db['entity_type'].isin(ents_todo['entity_type'])].copy() # keep only entities selected with this model
      db['entity_type'] = db['entity_type'].replace({'person':'PERSONA','address':'INDIRIZZO','organization':'ORGANIZZAZIONE', 'email':'E-MAIL', 'age':'ETÀ', 'fiscal_code':'CF', 'zipcode':'CAP', 'telephone':'TELEFONO'})
      if concat: self.dbs = pd.concat((self.dbs, db))
      self.tracker.loc[self.tracker['entity_type'].isin(ents_todo['entity_type']),'status']=True # set detected entities as done
      return db
    else:
      return empty_db() # entities already found by another Find call of the same model


if __name__ == '__main__':
  example = ''' In data 28/06/2022 abbiamo visitato il sig. Carlos Sieros di anni 66
  con zip code 50134 e anche 40120
  affetto da cardiomiopatia cronica all'ospedale Santa Maria delle Croci di Ravenna. Il signore lavora da Google.
  Il 10 9 2021 ha avuto un intervento chirurgico.  marina-61@virgilio.it.
  Il sign. Rossi ha come numero di telefono di casa 0574 569852.
  Si rimanda al prossimo controllo in data 4/09/2022. Gennaio 2020.
  Il paziente era accompagnato dalla figlia Viola Rossi con telefono +39 355 7401545.
  Da prendere al bisogno 72 mg di aspirina 7 gennaio 2020.
  Il 12/22 c'è stato il sole
  Il paziente lascia il suo numero di cellulare: 3841202587 valido fino al 18 MARZO 2021.
  Cordiali saluti,
  Dr. Fazeelat Abdullah.
  CF FZLBDL97E20E102W
  345/4722110

  18 gennaio 2021
  Via di Roma 25, Milano 48125
  7-1-2000
  '''
  deid = anonymizer('./config.json')
  output = deid.deIdentificationIta(example)
  print(output)
  # print('output text:', output_dict['text'])
  # print('matches dataframe:', output_dict['match_dataframe'])
  # print(deid.mask_data(example, mode='tag_l',date_level='month',sc='-')) # example of just masking using different modes with already stored found entities
  # deid.load_dict({'models':{'person':'spacy','telephone':'john'}}) # example of loading different models (non-passed parameters are not changed)
