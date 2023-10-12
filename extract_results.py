from abc import ABC, abstractmethod 
import pandas as pd 
import re 
import os 
import ast
from argparse import ArgumentParser
from src.utils import has_numbers

class Extracter(ABC):

    def __init__(self,input_dir,model) -> None:
        super().__init__()
        self.file_dir = input_dir
        self.model = model
        self.df = self.load_data()
        self.constructs = list(self.df['Construct'].unique())
        self.group =list(self.df['Group'].unique())
    
    @staticmethod
    def search_index(list_txt, string=None,pattern=None):
        search = []
        if pattern: 
            if type(pattern)==str:
                pattern = [pattern]
            for i,s in enumerate(list_txt):
                for match in pattern: 
                    if re.findall(match,s):
                        search.append(i)
                        break
            return search

        if type(string)==str:
            for i,s in enumerate(list_txt):
                if string in s:
                    search.append(i)
        if type(string)==list:
            for i, s in enumerate(list_txt):
                if [s for x in string if x in s]:
                    search.append(i)
        return search

    def load_data(self):
        return pd.read_csv(f'result/{self.file_dir}',index_col=[0])

    @abstractmethod
    def extract_keywords(self):
        pass 

    @abstractmethod
    def extract_reasons(self):
        pass

    @abstractmethod 
    def extract_ratings(self):
        pass

    @abstractmethod 
    def extract_overall_rating(self):
        pass 

    @abstractmethod
    def extract_openended(self):
        pass
    
    @abstractmethod
    def extract_emotion(self):
        pass

    @abstractmethod
    def extract_behavior(self):
        pass
    
    @abstractmethod
    def extract_socialconst(self):
        pass

    @abstractmethod
    def save_results_to_df(self,outdir):
        pass 

    @abstractmethod
    def convert_results_to_df(self):
        pass

class GPT35_Result(Extracter):
    
    def __init__(self, input_dir,model='gpt-3.5-turbo') -> None:
        super().__init__(input_dir,model)
        self.search_index = Extracter.search_index
        self.keyword_patterns = [r'\d.\s+(.*)',r'-\s+(.*)',r'-(.*)',r'\d\)(.*)']
        self.extra_patterns = [r'(.*)\s+\((.*)\)',r'(\w+):\s+(.*)',r'(.*)-\s+(.*)']
        self.reason_patterns=[r'\d.\s+(.*)',r'\-\s+(.*)']
        self.rating_patterns =[r'\-\s+(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'\-(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'\d.\s+(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)']

    def extract_keywords(self,sample,extra=False):
        extracted=[]
        extra_process=[]
        if len(sample)==1:
            if 'Keywords:' in sample[0]:
                sample=sample[0].split('.')
                if len(sample)==1:
                    extracted = sample[0].split('Keywords:')[1].strip().split(',')
                else:
                    extracted = sample[0].split('Keywords:')[1].strip().split(',')
                    if sample[1:]!=[' ']:
                        extra_process=[x for x in sample[1:] if x!='']
            else:
                if len([t for t in sample[0].split(',') if (t!='' and t!=' ')])>=1:
                    sample = sample[0].split(',')
                    for t in sample:
                        for pattern in self.keyword_patterns:
                            if re.findall(pattern, t): 
                                extracted.append(re.findall(pattern,t)[0])
                                break
                        
        else:
            if 'Keywords' in sample[0]:
                if len([t for t in sample[0].split('Keywords:') if (t!='' and t!='Keywords:' and t!=' ')])>=1: 
                    try:
                        extracted = sample[0].split('Keywords:')[1].strip().split(',')
                        if sample[1:]!=[' ']:
                            extra_process=[x for x in sample[1:] if (x!='' and 'Rating' not in x)]
                    except:
                        pass
                else:
                    sample=sample[1:]
                for t in sample:
                    if t.strip()=='Keywords:':
                        continue
                    for pattern in self.keyword_patterns:
                        if re.findall(pattern,t):
                            #print(re.findall(pattern,t))
                            extracted.append(re.findall(pattern,t)[0])
                            break
            else:
                for t in sample:
                    for pattern in self.keyword_patterns:
                        if re.findall(pattern,t):
                            #print(re.findall(pattern,t))
                            extracted.append(re.findall(pattern,t)[0])
                            break
        if extra: 
            for k,t in enumerate(extracted):
                for pattern in self.extra_patterns:
                    if re.findall(pattern,t):
                        extracted[k] = re.findall(pattern,t)[0][0]
                        extra_process.append(re.findall(pattern,t)[0][1])
                        break
        
        if extracted==[]:
            if re.findall(r'Keywords.*:\s+(.*)',sample[0]):
                extracted = re.findall(r'Keywords.*:\s+(.*)',sample[0])
            elif re.findall(r'Verbs\s+.*:(.*)',sample[0]):
                extracted = re.findall(r'Verbs\s+.*:(.*)',sample[0])
                extracted = extracted[0].strip().split(',')
                if len(sample)>1:
                    extracted.extend([t.strip() for t in sample[1:] if t!=''])
            elif 'Verbs:' in sample[0]:
                extracted = sample[0].split('Verbs:')[1].strip().split(',')
                if len(sample)>1:
                    extracted.extend([t.strip() for t in sample[1:] if t!=''])
            #print(sample)
        else:
            extracted=[x.strip() for x in extracted]

        if extra_process!=[]:
            extracted.append(extra_process)
        
        return extracted

    def extract_reasons(self,sample):
        extracted = []
        for i,t in enumerate(sample):
            s=[t for t in t.split('.') if t !='']
            for k, text in enumerate(s):
                if (text ==' ') or (text=='') or (text.isdigit()):
                    continue 
                if ('Ratings:' in text) or ('Rating:' in text) or('-Rating' in text): 
                    continue
                if ':'  in text: 
                    if (text.split(':')[1]=='') or (text.split(':')[1]==' '):
                        continue
                    else:
                        extracted.append(text.split(':')[1].strip())
                    continue
                found = False 
                for pattern in self.reason_patterns:
                    if re.findall(pattern, text):
                        extracted.append(re.findall(pattern,text)[0])
                        found=True
                        break
                if not found:
                    extracted.append(text.strip())            
        return extracted

    def extract_overall_rating(self,sample):
        for t in sample:
            if re.findall(r'Overall.*:.*((?<!\d|\.)\d+(?:\.\d+)?)',t):
                return re.findall(r'Overall.*:.*((?<!\d|\.)\d+(?:\.\d+)?)',t)[0]
            else:
                return []

    def extract_ratings(self,sample):
        extracted={}
        if len(sample)==1 and type(sample)==list:
                sample=sample[0].split(';')
        if len(sample)==1:
            for pattern in self.rating_patterns:
                res=re.findall(pattern,sample)
                if res: 
                    extracted[res[0][0].strip()]=res[0][1]
                    break
        else:
            for t in sample:
                for pattern in self.rating_patterns:
                    res = re.findall(pattern,t)
                    if res:
                        extracted[res[0][0].strip()]=res[0][1]
                        break
        return extracted

    def extract_openended(self):
        self.openended_results={'Keywords':[],'Reasons':[],'Ratings':[],'Overall_Rating':[],'Overall_Reasons':[]}
        for i, row in self.df.query("Construct=='OPENENDED'").iterrows():
            to_extract = [s for s in row['Answer'].split('\n') if s!='']
            
            idxs = [0] 
            
            rating_start = self.search_index(to_extract,'Friendly:')
            if rating_start ==[]:
                print(i,rating_start,to_extract)
                for k in self.openended_results.keys():
                    if k =='Ratings':
                        self.openended_results[k].append({})
                    else:
                        self.openended_results[k].append(['NaN'])
                continue
            rating_end = self.search_index(to_extract,'High-status:')

            reason_idxs=self.search_index(to_extract,['Reason','Reasoning' ,'reason'])
            overall_rating = self.search_index(to_extract,['Overall rating','Overall Rating'])

            if len(reason_idxs)==1:
                if int(reason_idxs[0])<int(rating_start[0]):
                    idxs.append(reason_idxs[0])
                    idxs.append(rating_start[0])
                    idxs.append(overall_rating[0])
                    idxs.append('')
                else:
                    idxs.append('')
                    idxs.append(rating_start[0])
                    idxs.append(overall_rating[0])
                    idxs.append(reason_idxs[0])

            elif len(reason_idxs)==2:
                idxs.append(reason_idxs[0])
                idxs.append(rating_start[0])
                idxs.append(overall_rating[0])
                idxs.append(reason_idxs[1])
            else:
                if reason_idxs:
                    if int(reason_idxs[0])<int(rating_start[0]):
                        idxs.append(reason_idxs[0])
                        idxs.append(rating_start[0])
                        idxs.append(overall_rating[0])
                    if reason_idxs[1]-reason_idxs[0]==1:
                        idxs.append(reason_idxs[2])
                    else: 
                        idxs.append(reason_idxs[1])
                else:
                    idxs.append(0)
                    idxs.append(rating_start[0])
                    idxs.append(overall_rating[0])
                    idxs.append(overall_rating[0])
                    
            if idxs[1]=='':
                keywords=self.extract_keywords(to_extract[idxs[0]:idxs[2]],extra=True)
                if type(keywords[-1])==list:
                    reasons = keywords[-1]
                    keywords = keywords[:-1]
            else:
                try:
                    keywords=self.extract_keywords(to_extract[idxs[0]:idxs[1]])
                    reasons = self.extract_reasons(to_extract[idxs[1]:idxs[2]])
                except:
                    keywords=[]
                    reasons=[]

            if keywords:
                self.openended_results['Keywords'].append(keywords)
            else:
                self.openended_results['Keywords'].append(['NaN'])
            if reasons: 
                self.openended_results['Reasons'].append(reasons)
            else:
                self.openended_results['Reasons'].append(['NaN'])
            
            #print(i,to_extract[idxs[2]:idxs[3]])
            ratings=self.extract_ratings(to_extract[idxs[2]:idxs[3]])
            if ratings:
                if 'status' in ratings.keys():
                    ratings['High-status']=ratings.pop('status')
                self.openended_results['Ratings'].append(ratings)
            else:
                self.openended_results['Ratings'].append({})

            if idxs[4]=='':
                overall_rating = self.extract_overall_rating(to_extract[idxs[3]:])
            else:
                overall_rating = self.extract_overall_rating(to_extract[idxs[3]:idxs[4]])
                reasons_2 = self.extract_reasons(to_extract[idxs[4]:])
            
            self.openended_results['Overall_Rating'].append([overall_rating])
            if reasons_2:
                self.openended_results['Overall_Reasons'].append(reasons_2)
            else:
                self.openended_results['Overall_Reasons'].append(['NaN'])

    def extract_emotion(self):
        self.emotion_results={'Keywords':[],'Reasons':[],'Ratings':[]}
        for i, row in self.df.query("Construct=='Emotion'").iterrows():
            to_extract = [s for s in row['Answer'].split('\n') if s!='']

            idxs = [0]
            rating_start=self.search_index(to_extract,'Contempt')
            keywords=[]
            reasons=[]
            ratings={}
            if rating_start==[]:
                keywords = self.extract_keywords(to_extract,extra=True)
                if keywords:
                    if type(keywords[-1])==list:
                        reasons = keywords[-1]
                        keywords = keywords[:-1]
                    else:
                        reasons = ['NaN']
                    self.emotion_results['Keywords'].append(keywords)
                    self.emotion_results['Reasons'].append(reasons)
                    self.emotion_results['Ratings'].append({})
                else:
                    for k in self.emotion_results.keys():
                        if k =='Ratings':
                            self.emotion_results[k].append({})
                        else:
                            self.emotion_results[k].append(['NaN'])
                print(i,rating_start,to_extract)
                continue

            reason_idx=self.search_index(to_extract,['Reason','Reasoning' ,'reason'])
            
            if reason_idx==[] or (reason_idx[0]==idxs[0]):
                idxs.append('')
                idxs.append(rating_start[0]) 
            else:
                idxs.append(reason_idx[0])
                idxs.append(rating_start[0])

            if idxs[1]=='':
                keywords = self.extract_keywords(to_extract[idxs[0]:idxs[2]],extra=True)
                if type(keywords[-1])==list:
                    reasons=keywords[-1]
                    keywords=keywords[:-1]
            else:
                keywords=self.extract_keywords(to_extract[idxs[0]:idxs[1]])
                reasons=self.extract_reasons(to_extract[idxs[1]:idxs[2]])

            ratings = self.extract_ratings(to_extract[idxs[2]:])

            if keywords:
                self.emotion_results['Keywords'].append(keywords)
            else:
                self.emotion_results['Keywords'].append(['NaN'])
            if reasons:
                self.emotion_results['Reasons'].append(reasons)
            else:
                self.emotion_results['Reasons'].append(['NaN'])
            if ratings:
                if 'Admiration' in ratings.keys():
                    ratings['Admire']=ratings.pop('Admiration')
                if 'Pride' in ratings.keys():
                    ratings['Proud']=ratings.pop('Pride')
                if 'Envy' in ratings.keys():
                    ratings['Envious']=ratings.pop('Envy')
                if 'Jealousy' in ratings.keys():
                    ratings['Jealous']=ratings.pop('Jealousy')

                self.emotion_results['Ratings'].append(ratings)
            else:
                self.emotion_results['Ratings'].append({})

    def extract_behavior(self):
        self.behavior_results={'Keywords':[],'Reasons':[],'Ratings':[]}
        for i, row in self.df.query("Construct=='Behavior'").iterrows():
            to_extract = [s for s in row['Answer'].split('\n') if s!='']
            
            idxs = [0]
            rating_start=self.search_index(to_extract,pattern=r'Help.*:\s+((?<!\d|\.)\d+(?:\.\d+)?)')
            reason_idx=self.search_index(to_extract,['Reason','Reasoning' ,'reason'])
            if rating_start==[]:
                keywords=self.extract_keywords(to_extract,extra=True)
                if keywords:
                    if type(keywords[-1])==list:
                        reasons = keywords[-1]
                        keywords = keywords[:-1]
                    else:
                        reasons = ['NaN']
                    self.behavior_results['Keywords'].append(keywords)
                    self.behavior_results['Reasons'].append(reasons)
                    self.behavior_results['Ratings'].append({})
                else:
                    for k in self.behavior_results.keys():
                        if k =='Ratings':
                            self.behavior_results[k].append({})
                        else:
                            self.behavior_results[k].append(['NaN'])
                #print(i,rating_start,to_extract)
                continue

            if reason_idx==[] or (reason_idx[0]==idxs[0]):
                idxs.append('')
                idxs.append(rating_start[0])
            else:
                idxs.append(reason_idx[0])
                idxs.append(rating_start[0])
            

            #print(i,idxs,to_extract)
            if idxs[1]=='':
                if not to_extract[idxs[0]:idxs[2]]:
                    keywords=[]
                    reasons=[]
                else:
                    keywords=self.extract_keywords(to_extract[idxs[0]:idxs[2]],extra=True)
                    if type(keywords[-1])==list:
                        reasons = keywords[-1]
                        keywords = keywords[:-1]
            else:
                keywords=self.extract_keywords(to_extract[idxs[0]:idxs[1]])
                reasons=self.extract_reasons(to_extract[idxs[1]:idxs[2]])

            ratings_raw = self.extract_ratings(to_extract[idxs[2]:])
            ratings = {}
            to_remove = len(row['Group'].split(' '))
            for key in ratings_raw.keys(): 
                #print(key.split(' '))
                ratings[' '.join(key.split(' ')[:-to_remove])]=ratings_raw[key]

            if keywords:
                self.behavior_results['Keywords'].append(keywords)
            else:
                self.behavior_results['Keywords'].append(['NaN'])
            if reasons:
                self.behavior_results['Reasons'].append(reasons)
            else:
                self.behavior_results['Reasons'].append(['NaN'])
            if ratings:
                self.behavior_results['Ratings'].append(ratings)
            else:
                self.behavior_results['Ratings'].append({})

    def extract_socialconst(self):
        self.socialconst_results={'Keywords':[],'Reasons':[],'Ratings':[],'Type':[],'Group':[]}
        for group in self.group:
            for i, row in self.df.query("Construct=='Social structure' and Group==@group").iterrows():
                to_extract = [s for s in row['Answer'].split('\n') if s!='']
                rating_index = self.search_index(to_extract, pattern=r'Rating:\s+((?<!\d|\.)\d+(?:\.\d+)?)')
                if rating_index: 
                    rat=re.findall(r'Rating:\s+((?<!\d|\.)\d+(?:\.\d+)?)', to_extract[rating_index[0]])
                    if rat:
                        self.socialconst_results['Ratings'].append(rat[0])
                    else:
                        self.socialconst_results['Ratings'].append(['NaN'])
                else:
                    self.socialconst_results['Ratings'].append(['NaN'])

                reason_index=self.search_index(to_extract,['Reason','Reasoning' ,'reason'] )
                if reason_index:
                    keywords=self.extract_keywords(to_extract[reason_index[0]:],extra=True)
                    if keywords:
                        if type(keywords[-1])==list:
                            reasons=keywords[-1]
                            keywords=keywords[:-1]
                        else:
                            reasons=['NaN']
                        self.socialconst_results['Keywords'].append(keywords)
                        self.socialconst_results['Reasons'].append(reasons)
                    else:
                        self.socialconst_results['Keywords'].append(['NaN'])
                        self.socialconst_results['Reasons'].append(['NaN'])
                else:
                    self.socialconst_results['Keywords'].append(['NaN'])
                    self.socialconst_results['Reasons'].append(['NaN'])
                
                if 'economically' in row['Questionnaire']: 
                    self.socialconst_results['Type'].append('Economically Successful')
                elif 'prestigious' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Prestigious')
                elif 'special treatments' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Special Treatments')
                elif 'resources' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Resources')
                
                self.socialconst_results['Group'].append(group)
                
    def convert_results_to_df(self,result):
        if 'Ratings' in result.keys():
            r=pd.DataFrame(result['Ratings'])
            if 'Group' not in result.keys():
                r['Group']=self.group
        else:
            if 'Group' not in result.keys():
                r = pd.DataFrame(self.group,columns=['Group'])
        for k in result.keys():
            if k=='Ratings':
                continue
            r[k]=result[k]
        return r

    def save_results_to_df(self,outdir=None,result_to_convert=None):
        if not result_to_convert:
            result_to_convert=['openended','emotion','behavior','socialconstruct']
        if type(result_to_convert)==str:
            result_to_convert=[result_to_convert]

        for convert in result_to_convert:
            if convert=='openended':
                try:
                    self.openended_results
                except:
                    self.extract_openended()
                df = self.convert_results_to_df(self.openended_results)
            if convert=='emotion':
                try:
                    self.emotion_results
                except:
                    self.extract_emotion() 
                df = self.convert_results_to_df(self.emotion_results)
            if convert=='behavior':
                try:
                    self.behavior_results
                except:
                    self.extract_behavior() 
                df = self.convert_results_to_df(self.behavior_results)
            if convert=='socialconstruct':
                try:
                    self.socialconst_results
                except:
                    self.extract_socialconst()
                df = self.convert_results_to_df(self.socialconst_results)

            if outdir:
                df.to_csv('result/{outdir}')
                print(f"Saved to result/{outdir}")
            else:
                i=0
                base = f'processed_sscm_{self.model}_{convert}_{i}'
                while os.path.exists(f'result/{base}.csv'):
                    i+=1
                    base = f'processed_sscm_{self.model}_{convert}_{i}'
                df.to_csv(f'result/{base}.csv')
                print(f"Saved to result/{base}.csv!!")

class Bard_Result(Extracter):
    def __init__(self, input_dir, model='Bard') -> None:
        super().__init__(input_dir, model)
        self.search_index = Extracter.search_index
        self.keyword_patterns = [r'\*\*(\w+(?:-\w+)*):\*\*',r'\*\s+\*\*(\w+(?:-\w+)*)\*\*\s+-',
                  r'\*\s+(\w+(?:-\w+)*)',r'\*\s+\*\*(\w+(?:-\w+)*)\*\*.',r'\*\s+\*\*(\w+(?:-\w+)*)\*\*',
                  r'\*\*(\w+(?:-\w+)*)\*\*',r'\*\s+\*\*(\w+(?:-\w+)*):\*\*']
        self.extra_patterns = [r'\*\*\w+(?:-\w+)*:\*\*\s(.*)',r'\*\s\*\*\w+(?:-\w+)*\*\*\s+-\s(.*)',r'\*\s+\*\*\w+(?:-\w+)*\*\*.\s+(.*)',r'\*\s+\*\*\w+(?:-\w+)*:\*\*\s+(.*)']
        self.reason_patterns=[r'\*\s+\*\*\w+(?:-\w+)*:\*\*\s+(.*)',r'\*\s+(.*)',r'\*\s+\*\*(.*)\*\*\s+(.*)',r'\d.\s+(.*)']
        self.rating_patterns =[r'\*\s+(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'\n\|\s+(.*)\s+\|\s+((?<!\d|\.)\d+(?:\.\d+)?)\s+\|',r'\*\*(.*):.*((?<!\d|\.)\d+(?:\.\d+)?)',r'\n(.*)\s+\|\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'\*\s+\*\*(.*)\*\*\s+-\s+((?<!\d|\.)\d+(?:\.\d+)?)']

    def extract_ratings(self,sample):
        extracted={}
        ratings=[]
        for pattern in self.rating_patterns:
            if re.findall(pattern, sample):
                ratings=re.findall(pattern,sample)
                #print(ratings)
                break
        if ratings:
            for element in ratings:
                extracted[element[0]]=element[1]
        else:
            return {}
        return extracted 

    def extract_keywords(self,sample,extra=True):
        keywords=[]
        extra_extracted=[]

        if type(sample)==str:
            sample=[sample]
        found = False
        for i,t in enumerate(sample):
            found=False
            for pattern in self.keyword_patterns:
                if re.findall(pattern,t):
                    found=True
                    keywords.extend(re.findall(pattern,t))
                    break
            if extra:
                extra_found=False
                for pattern in self.extra_patterns:
                    if re.findall(pattern,t):
                        extra_found=True
                        extra_extracted.extend(re.findall(pattern,t))
                        break
                if (not found) and (keywords!=[]) and (not extra_found) and ('rating' not in t) :
                    extra_extracted.append(t)
        
        if keywords==[]:
            print('NOTFOUND')
        if extra_extracted:
            keywords.append(extra_extracted)
        
        return keywords
    
    def extract_reasons(self,sample):
        extracted=[]
        for t in sample:
            for pattern in self.reason_patterns:
                res = re.findall(pattern,t)
                if res:
                    if type(res[0])==tuple:
                        extracted.extend([x for x in res[0]])
                    else:
                        extracted.extend(res)
                    break
        
        extracted=[x for x in extracted if ('Reason' not in x) and ('reason' not in x)]
        return extracted
    
    def extract_overall_rating(self,sample):
        overall_patterns=[r'\*\s+\*\*Overall\s+rating:\*\*\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
        r'(?<=Overall rating).*:\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'(?<=Overall rating):\s+((?<!\d|\.)\d+(?:\.\d+)?)']
        if type(sample)==str:
            sample = [sample]
        for t in sample:
            for match in overall_patterns:
                if re.findall(match,t):
                    #print(re.findall(match,t))
                    return re.findall(match,t)
                    break
        return []

    def extract_socialconst(self):
        self.socialconst_results={'Keywords':[],'Reasons':[],'Ratings':[],'Type':[],'Group':[]}
        col_to_compute=[col for col in list(self.df.columns) if col not in ['Group','Construct','Attribute','Questionnaire']]
        patterns = [r"On\sa\sscale\sof\s1\sto\s5.*a\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                    r"((?<!\d|\.)\d+(?:\.\d+)?)\s+out of 5",
                    r"\*\*Rating:\s+((?<!\d|\.)\d+(?:\.\d+)?)\*\*",r"((?<!\d|\.)\d+(?:\.\d+)?)\s+on\sa\s5-point\sscale",
                    r"I\swould\srate.*as\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                    r"Rating:\s+((?<!\d|\.)\d+(?:\.\d+)?)",r"\*\*Rating:\*\*\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                    r"I\swould\srate\sthem\sa\s+((?<!\d|\.)\d+(?:\.\d+)?)",r"((?<!\d|\.)\d+(?:\.\d+)?)\son\sa\sscale\sof\s1\sto\s5"]
        custom_keywords = [r'\*\s+\*\*(.*):\*\*',r'\*\s+\*\*(.*)\*\*',r'\*\*Keywords:\*\*\s+(.*),\s+(.*),\s+(.*)',r'Keywords:\s+(.*),\s+(.*),\s+(.*)',r'\*\s+(.*)\n']
        custom_reasons = [r'\*\s+\*\*.*:\*\*\s(.*)',r'\*\s+\*\*.*\*\*\s+(.*)',r'(?<=First,)\s+(.*)\s+Second,\s+(.*)\s+Third,\s+(.*)',r'(?<=First,)\s+(.*)\s+Second,\s+(.*)',r'(?<=First,)\s+(.*)',r'(?<=Second,)\s+(.*)',r'(?<=Third,)\s+(.*)',r'\*\s+(.*)\n']

        for group in self.group:
            for i, row in self.df.query("Construct=='Social structure' and Group==@group").iterrows():
                for col in col_to_compute:
                    if col=='Answer':
                        to_extract = [s for s in row['Answer'].split('\n\n') if s!='']
                    else:
                        if str(row[col])!='nan':
                            to_extract = [s for s in ast.literal_eval(row[col])[0].split('\n\n') if s!='']
                        else:
                            continue
                                                            
                    rating_idx = self.search_index(to_extract,pattern=patterns)
                    
                    ratings = None
                    if rating_idx:
                        for pattern in patterns: 
                            if re.findall(pattern,to_extract[rating_idx[0]]):
                                ratings = re.findall(pattern,to_extract[rating_idx[0]])[0]
                                break

                        to_extract.pop(rating_idx[0])
                        #print(to_extract)
                        keyword_idx = self.search_index(to_extract,['keyword','Keyword'])
                        #reason_idx = search_index(to_extract,['Reason','reason','Reasoning','factor'])

                        keywords= []
                        reasons= [] 
                        if keyword_idx:
                            for t in to_extract[keyword_idx[0]:]:
                                for pattern in custom_keywords:
                                    k_pattern = re.findall(pattern,t)
                                    if k_pattern:
                                        if type(k_pattern[0])==tuple:
                                            keywords.extend([k for k in k_pattern[0]])
                                        else:
                                            keywords.extend(k_pattern)
                                        break
                            for t in to_extract:
                                for pattern_reason in custom_reasons:
                                    r_pattern = re.findall(pattern_reason,t)
                                    if r_pattern:
                                        if type(r_pattern[0])==tuple:
                                            reasons.extend([r for r in r_pattern[0]])
                                        else:
                                            reasons.extend(re.findall(pattern_reason,t))
                                        break
                                
                        else:
                            #print(i,col,to_extract)
                            for t in to_extract:
                                for pattern in custom_keywords:
                                    k_pattern = re.findall(pattern,t)
                                    if k_pattern:
                                        if type(k_pattern[0])==tuple:
                                            keywords.extend([k for k in k_pattern[0]])
                                        else:
                                            keywords.extend(k_pattern)
                                        break
                            for t in to_extract:
                                for pattern_reason in custom_reasons:
                                    r_pattern = re.findall(pattern_reason,t)
                                    if r_pattern:
                                        if type(r_pattern[0])==tuple:
                                            reasons.extend([r for r in r_pattern[0]])
                                        else:
                                            reasons.extend(re.findall(pattern_reason,t))
                                        break
                        if ratings: 
                            self.socialconst_results['Ratings'].append(ratings)
                        else:
                            self.socialconst_results['Ratings'].append('NaN')
                        if keywords:
                            self.socialconst_results['Keywords'].append(keywords)
                        else:
                            self.socialconst_results['Keywords'].append(['NaN'])
                        if reasons:
                            self.socialconst_results['Reasons'].append(reasons)
                        else:
                            self.socialconst_results['Reasons'].append(['NaN'])
                    else:
                        self.socialconst_results['Ratings'].append('NaN')
                        self.socialconst_results['Keywords'].append(['NaN'])
                        self.socialconst_results['Reasons'].append(['NaN'])
                    
                    if 'economically' in row['Questionnaire']: 
                        self.socialconst_results['Type'].append('Economically Successful')
                    elif 'prestigious' in row['Questionnaire']:
                        self.socialconst_results['Type'].append('Prestigious')
                    elif 'special treatments' in row['Questionnaire']:
                        self.socialconst_results['Type'].append('Special Treatments')
                    elif 'resources' in row['Questionnaire']:
                        self.socialconst_results['Type'].append('Resources')
                    self.socialconst_results['Group'].append(group)

    def extract_behavior(self):
        self.behavior_results={'Keywords':[],'Reasons':[],'Ratings':[],'Group':[]}
        col_to_compute=[col for col in list(self.df.columns) if col not in ['Group','Construct','Attribute','Questionnaire']]
        for i, row in self.df.query("Construct=='Behavior'").iterrows():
            for col in col_to_compute:
                if col=='Answer':
                    to_extract = [s for s in row['Answer'].split('\n\n') if s!='']
                else:
                    if str(row[col])!='nan':
                        to_extract = [s for s in ast.literal_eval(row[col])[0].split('\n\n') if s!='']
                    else:
                        continue
                
                rating_idx = self.search_index(to_extract,pattern=[r"\*\s+Help\s(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                r"\|\s+Help\s(.*)\s\|\s((?<!\d|\.)\d+(?:\.\d+)?)",r"\*\*Help\s(.*):\*\*\s((?<!\d|\.)\d+(?:\.\d+)?)",r"\n\|\s+Help\s+\|",
                r"\*\*Help:\*\*\s+((?<!\d|\.)\d+(?:\.\d+)?)",r"\nHelp\s\|\s+((?<!\d|\.)\d+(?:\.\d+)?)",r"\*\s+\*\*Help\*\*\s+-\s+((?<!\d|\.)\d+(?:\.\d+)?)"])
                
                keywords=[]
                reasons=[]
                ratings=None
                if rating_idx:
                    ratings=self.extract_ratings(to_extract[rating_idx[0]])                
                    reason_idx = self.search_index(to_extract[:rating_idx[0]],['Reason','reason','Reasoning'])
                    
                    if reason_idx and reason_idx[0] in [0,1]:
                        reason_idx=[]
                    
                    if not reason_idx:
                    #    print(to_extract[:rating_idx[0]])
                        keywords=self.extract_keywords(to_extract[:rating_idx[0]],extra=True)
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                            
                    else:
                        #print(to_extract[:reason_idx[0]])
                        keywords=self.extract_keywords(to_extract[:reason_idx[0]],extra=True)
                        reasons=[]
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                            #print(i,to_extract[reason_idx[0]:rating_idx[0]])
                        reasons.extend(self.extract_reasons(to_extract[reason_idx[0]:rating_idx[0]]))

                    if ratings: 
                        ratings_refined = {} 
                        for key in ratings.keys():
                            ratings_refined[key.split(' ')[0]]=ratings[key]

                        self.behavior_results['Ratings'].append(ratings_refined)
                    else:
                        self.behavior_results['Ratings'].append({})
                    if keywords:
                        self.behavior_results['Keywords'].append(keywords)
                    else:
                        self.behavior_results['Keywords'].append(['NaN'])
                    if reasons:
                        self.behavior_results['Reasons'].append(reasons)
                    else:
                        self.behavior_results['Reasons'].append(['NaN'])

                else:
                    self.behavior_results['Ratings'].append({})
                    self.behavior_results['Keywords'].append(['NaN'])
                    self.behavior_results['Reasons'].append(['NaN'])
                
                self.behavior_results['Group'].append(row['Group'])

    def extract_emotion(self):
        self.emotion_results={'Keywords':[],'Reasons':[],'Ratings':[],'Group':[]}
        col_to_compute=[col for col in list(self.df.columns) if col not in ['Group','Construct','Attribute','Questionnaire']]
        for i, row in self.df.query("Construct=='Emotion'").iterrows():
            for col in col_to_compute:
                if col=='Answer':
                    to_extract = [s for s in row['Answer'].split('\n\n') if s!='']
                else:
                    if str(row[col])!='nan':
                        to_extract = [s for s in ast.literal_eval(row[col])[0].split('\n\n') if s!='']
                    else:
                        continue
                
                rating_idx = self.search_index(to_extract,pattern=[r"\*\s+Contempt:\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                r"\|\s+Contempt\s\|\s((?<!\d|\.)\d+(?:\.\d+)?)",r"\*\*Contempt:\*\*\s((?<!\d|\.)\d+(?:\.\d+)?)"])
                
                if rating_idx:
                    ratings=self.extract_ratings(to_extract[rating_idx[0]])
                
                    reason_idx = self.search_index(to_extract[:rating_idx[0]],['Reason','reason','Reasoning'])
                    if reason_idx and reason_idx[0] in [0,1]:
                        reason_idx=[]
                    keywords=[]    
                    if not reason_idx:
                    #    print(to_extract[:rating_idx[0]])
                        keywords=self.extract_keywords(to_extract[:rating_idx[0]],extra=True)
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                            
                    else:
                        #print(to_extract[:reason_idx[0]])
                        keywords=self.extract_keywords(to_extract[:reason_idx[0]],extra=True)
                        reasons=[]
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                            #print(i,to_extract[reason_idx[0]:rating_idx[0]])
                        reasons.extend(self.extract_reasons(to_extract[reason_idx[0]:rating_idx[0]]))

                    if ratings: 
                        self.emotion_results['Ratings'].append(ratings)
                    else:
                        self.emotion_results['Ratings'].append({})
                    if keywords:
                        self.emotion_results['Keywords'].append(keywords)
                    else:
                        self.emotion_results['Keywords'].append(['NaN'])
                    if reasons:
                        self.emotion_results['Reasons'].append(reasons)
                    else:
                        self.emotion_results['Reasons'].append(['NaN'])

                else:
                    self.emotion_results['Ratings'].append({})
                    self.emotion_results['Keywords'].append(['NaN'])
                    self.emotion_results['Reasons'].append(['NaN'])
                
                self.emotion_results['Group'].append(row['Group'])

    def extract_openended(self):
        self.openended_results={'Keywords':[],'Reasons':[],'Ratings':[],'Overall_Rating':[],'Overall_Reasons':[],'Group':[]}
        col_to_compute=[col for col in list(self.df.columns) if col not in ['Group','Construct','Attribute','Questionnaire']]
        for i, row in self.df.query("Construct=='OPENENDED'").iterrows():
            for col in col_to_compute:
                if col=='Answer':
                    to_extract = [s for s in row['Answer'].split('\n\n') if s!='']
                else:
                    if str(row[col])!='nan':
                        to_extract = [s for s in ast.literal_eval(row[col])[0].split('\n\n') if s!='']
                    else:
                        continue
                    
                #to_extract = [s for s in row['Answer'].split('\n\n') if s!='']
                #print(to_extract)
                #print(i,col,to_extract)
                rating_idx = self.search_index(to_extract,pattern=[r"\*\s+Friendly:\s+((?<!\d|\.)\d+(?:\.\d+)?)",
                r"\|\s+Friendly\s\|\s((?<!\d|\.)\d+(?:\.\d+)?)",r"\*\*Friendly:\*\*\s((?<!\d|\.)\d+(?:\.\d+)?)"])
                if rating_idx:
                    ratings=self.extract_ratings(to_extract[rating_idx[0]])

                    keywords=[]
                    reason_idx = self.search_index(to_extract[:rating_idx[0]],['Reason','reason','Reasoning'])
                    if not reason_idx:
                    #    print(to_extract[:rating_idx[0]])
                        keywords=self.extract_keywords(to_extract[:rating_idx[0]],extra=True)
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                            
                    else:
                        #print(to_extract[:reason_idx[0]])
                        keywords=self.extract_keywords(to_extract[:reason_idx[0]],extra=True)
                        reasons=[]
                        if keywords:
                            if type(keywords[-1])==list:
                                reasons=keywords[-1]
                                keywords=keywords[:-1]
                        reasons.extend(self.extract_reasons(to_extract[reason_idx[0]:rating_idx[0]]))
                    
                    if ratings:
                        col_patterns =[r'\*\s+(\w+(?:-\w+)*)','\|\s+(\w+(?:-\w+)*)']
                        cols = list(ratings.keys())
                        for key in cols:
                            for patt in col_patterns:
                                if re.findall(patt,key):
                                    value=ratings.pop(key)
                                    ratings[re.findall(patt,key)[0]]=value
                                    break
                        self.openended_results['Ratings'].append(ratings)
                    else:
                        self.openended_results['Ratings'].append({})
                    if keywords:
                        self.openended_results['Keywords'].append(keywords)
                    else:
                        self.openended_results['Keywords'].append(['NaN'])
                    if reasons:
                        self.openended_results['Reasons'].append(reasons)
                    else:
                        self.openended_results['Reasons'].append(['NaN'])
                
                    overall_index = self.search_index(to_extract,['Overall rating','Overall Rating','Overall']) # Overall, I would rate 
                    overall_rating=[]
                    overall_reason=[]
                    if overall_index:
                        #print(i,to_extract[overall_index[0]])
                        overall_rating=self.extract_overall_rating(to_extract[overall_index[0]])
                        if overall_rating==[]:
                            #print(i,to_extract[overall_index[0]:])
                            overall_reason=self.extract_reasons(to_extract[overall_index[0]:])
                        #    continue
                        else:
                            overall_reason=self.extract_reasons(to_extract[overall_index[0]+1:])
                    else:
                        overall_rating=self.extract_overall_rating(to_extract[rating_idx[0]+1:])
                        overall_reason=self.extract_reasons(to_extract[rating_idx[0]+1:])

                    if overall_rating:
                        self.openended_results['Overall_Rating'].append(overall_rating[0])
                    else:
                        self.openended_results['Overall_Rating'].append('NaN')
                    
                    if overall_reason:
                        self.openended_results['Overall_Reasons'].append(overall_reason)
                    else:
                        self.openended_results['Overall_Reasons'].append(['NaN'])
                else:
                    self.openended_results['Ratings'].append({})
                    self.openended_results['Keywords'].append(['NaN'])
                    self.openended_results['Reasons'].append(['NaN'])
                    self.openended_results['Overall_Rating'].append('NaN')
                    self.openended_results['Overall_Reasons'].append(['NaN'])
                
                self.openended_results['Group'].append(row['Group'])

    def convert_results_to_df(self,result):
        if 'Ratings' in result.keys():
            if type(result['Ratings'][0])!=dict: 
                r=pd.DataFrame(result['Ratings'],columns=['Ratings'])
            else:
                r=pd.DataFrame(result['Ratings'])
            if 'Group' not in result.keys():
                r['Group']=self.group
        else:
            if 'Group' not in result.keys():
                r = pd.DataFrame(self.group,columns=['Group'])
        for k in result.keys():
            if k=='Ratings':
                continue
            r[k]=result[k]
        return r

    def save_results_to_df(self,outdir=None,result_to_convert=None):
        if not result_to_convert:
            result_to_convert=['openended','emotion','behavior','socialconstruct']
        if type(result_to_convert)==str:
            result_to_convert=[result_to_convert]

        for convert in result_to_convert:
            if convert=='openended':
                try:
                    self.openended_results
                except:
                    self.extract_openended()
                df = self.convert_results_to_df(self.openended_results)
            if convert=='emotion':
                try:
                    self.emotion_results
                except:
                    self.extract_emotion() 
                df = self.convert_results_to_df(self.emotion_results)
            if convert=='behavior':
                try:
                    self.behavior_results
                except:
                    self.extract_behavior() 
                df = self.convert_results_to_df(self.behavior_results)
            if convert=='socialconstruct':
                try:
                    self.socialconst_results
                except:
                    self.extract_socialconst()
                df = self.convert_results_to_df(self.socialconst_results)

            if outdir:
                df.to_csv('result/{outdir}')
                print(f"Saved to result/{outdir}")
            else:
                i=0
                base = f'processed_sscm_{self.model}_{convert}_{i}'
                while os.path.exists(f'result/{base}.csv'):
                    i+=1
                    base = f'processed_sscm_{self.model}_{convert}_{i}'
                df.to_csv(f'result/{base}.csv')
                print(f"Saved to result/{base}.csv!!")
            
class Davinci_Result(Extracter):
    def __init__(self, input_dir, model='text-davinci-003') -> None:
        super().__init__(input_dir, model)
        self.search_index = Extracter.search_index
        self.keyword_patterns = [r'\d\.\s+(\w+(?:-\w+)*)\s+-\s+',r'\d\.\s+(\w+(?:-\w+)*):', r'(\w+(?:-\w+)*),\s+(\w+(?:-\w+)*),\s+and\s+(\w+(?:-\w+)*)',r'(\w+(?:-\w+)*?)\s+(?=\(.*\))',
                    r'\d\.\s+(\w+(?:-\w+)*)',r'Keywords:\s+(.*?),\s+(.*?),\s+(.*)\s-',r'Keywords:\s+(.*?),\s+(.*?),\s+(.*)',r'\d\.\s+(.*):',r'(\w+(?:-\w+)*?)\s+-\s+',
                    r'(^(?:(?!Rating|Keywords|Reasons)\w+(?:-\w+)*)):']
        self.extra_patterns = [r'\d\.\s+\w+(?:-\w+)*\s+-\s+(.*)',r'\d\.\s+\w+(?:-\w+)*:\s(.*)',r'(?<=\()(.*?)(?=\))',]
        self.reason_patterns=[r'\d\)\s+(.*)',r'\d.\s+(.*)',r'Description:\s(.*)',r'(?<!Keywords)(?<!Rating):\s+(.*)',r'Keywords:\s.*\s+-(.*)']
        self.rating_patterns =[r'(.*):\s+((?<!\d|\.)\d+(?:\.\d+)?)']
        self.overall_patterns=[r'^((?<!\d|\.)\d+(?:\.\d+)?)\s-',r'((?<!\d|\.)\d+(?:\.\d+)?)\son\sthe\s5-point\sscale',r'((?<!\d|\.)\d+(?:\.\d+)?)\s+out\sof5',r'rate.*as\s+a\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'rate.*at\s+a\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'rate.*a\s+((?<!\d|\.)\d+(?:\.\d+)?)',r'Overall\srating:\s+((?<!\d|\.)\d+(?:\.\d+)?)',
                      r'rate.*at\s+((?<!\d|\.)\d+(?:\.\d+)?)\s+out\sof\s5',r'Overall\sRating:\s+((?<!\d|\.)\d+(?:\.\d+)?)',
                      r'((?<!\d|\.)\d+(?:\.\d+)?)\sout\sof\s5',r'Rating:\s+((?<!\d|\.)\d+(?:\.\d+)?)',
                      r'The\srating.*((?<!\d|\.)\d+(?:\.\d+)?)/5',
                      r'The\srating.*((?<!\d|\.)\d+(?:\.\d+)?)',r'((?<!\d|\.)\d+(?:\.\d+)?)/5',r'^((?<!\d|\.)\d+(?:\.\d+)?)$']


    def extract_keywords(self,sample,extra=True):
        keywords=[]
        extra_extracted=[]

        if type(sample)==str:
            sample = [sample]
        for t in sample:
            for pattern in self.keyword_patterns:
                res = re.findall(pattern,t)
                if res:
                    if type(res[0])==tuple:
                        keywords.extend([k for k in res[0]])
                    else:
                        keywords.extend(res)
                    break

            for ex_pattern in self.extra_patterns:
                if re.findall(ex_pattern,t):
                    extra_extracted.extend(re.findall(ex_pattern,t))
                    break
        if extra_extracted:
            keywords.append(extra_extracted)
        return keywords    
        
    def extract_reasons(self,sample):
        reasons=[]
        if type(sample)==str:
            sample = [sample]
        for t in sample:
            for pattern in self.reason_patterns:
                res = re.findall(pattern,t)
                if res:
                    if type(res[0])==tuple:
                        reasons.extend([k for k in res[0]])    
                    else:
                        reasons.extend(res)
                    break
        reasons = [x for x in reasons if (x!='') and (x!=' ')]
        return reasons
    
    def extract_ratings(self,sample):
        extracted = {} 
        ratings = []

        if type(sample)==str:
            sample = [sample]
        for t in sample:
            for pattern in self.rating_patterns:
                res = re.findall(pattern,t)
                if res:
                    ratings=res
                    break
        if ratings:
            for element in ratings:
                extracted[element[0]]=element[1]
        else:
            return {}
        return extracted

    def extract_overall_rating(self,sample):
        if type(sample)==str:
            sample = [sample]
        for match in self.overall_patterns:
            for t in sample:
                if re.findall(match,t):
                    return re.findall(match,t)       
        return []

    def extract_emotion(self):
        self.emotion_results={'Keywords':[],'Reasons':[],'Ratings':[],'Group':[]}
        for group in self.group:
            self.emotion_results['Group'].append(group)
            for i, row in self.df.query("Construct=='Emotion' and Group==@group").iterrows():
                to_extract=[s for s in row['Answer'].split('\n\n') if s!='']
                keywords=[]
                reasons=[]
                ratings={}
                if "I am study" in row['Questionnaire']:
                    keywords=self.extract_keywords(to_extract)
                    if keywords:
                        if type(keywords[-1])==list:
                            reasons=keywords[-1]
                            keywords=keywords[:-1]
                            self.emotion_results['Reasons'].append(reasons)
                        else:
                            self.emotion_results['Reasons'].append(['NaN'])
                        self.emotion_results['Keywords'].append(keywords)
                    else:
                        self.emotion_results['Keywords'].append(['NaN'])
                        self.emotion_results['Reasons'].append(['NaN'])
                elif "rating" in row['Questionnaire']:
                    ### extract rating
                    ratings=self.extract_ratings(to_extract)
                    self.emotion_results['Ratings'].append(ratings)

    def extract_behavior(self):
        self.behavior_results={'Keywords':[],'Reasons':[],'Ratings':[],'Group':[]}
        for group in self.group:
            self.behavior_results['Group'].append(group)
            for i, row in self.df.query("Construct=='Behavior' and Group==@group").iterrows():
                to_extract=[s for s in row['Answer'].split('\n\n') if s!='']
                keywords=[]
                reasons=[]
                ratings={}
                ratings_refined = {}
                if "I am study" in row['Questionnaire']:
                    keywords=self.extract_keywords(to_extract)
                    if keywords:
                        if type(keywords[-1])==list:
                            reasons=keywords[-1]
                            keywords=keywords[:-1]
                            self.behavior_results['Reasons'].append(reasons)
                        else:
                            self.behavior_results['Reasons'].append(['NaN'])
                        self.behavior_results['Keywords'].append(keywords)
                    else:
                        self.behavior_results['Keywords'].append(['NaN'])
                        self.behavior_results['Reasons'].append(['NaN'])
                elif "rating" in row['Questionnaire']:
                    ### extract rating
                    ratings=self.extract_ratings(to_extract)
                    if ratings:
                        for key in ratings.keys():
                            ratings_refined[key.split(' ')[0]]=ratings[key]
                    self.behavior_results['Ratings'].append(ratings_refined)

    def extract_socialconst(self):
        self.socialconst_results={'Keywords':[],'Reasons':[],'Ratings':[],'Type':[],'Group':[]}
        for group in self.group:
            for i, row in self.df.query("Construct=='Social structure' and Group==@group").iterrows():
                to_extract=[s for s in row['Answer'].split('\n') if s!='']
                rating_index = self.search_index(to_extract,pattern=self.overall_patterns)
            
                rating=[]
                reasons=[]
                keywords=[]

                if rating_index:
                    rating=self.extract_overall_rating(to_extract[rating_index[0]])
                
                if rating: 
                    self.socialconst_results['Ratings'].append(rating)
                else:
                    self.socialconst_results['Ratings'].append(['NaN'])
                
                keywords=self.extract_keywords(to_extract) 
                if keywords:
                    if type(keywords[-1])==list:
                        reasons=[x for x in keywords[-1] if x not in ['extremely']]
                    keywords=[x for x in keywords[:-1]if x not in ['The','5','Description']]

                    self.socialconst_results['Keywords'].append(keywords)
                else:
                    self.socialconst_results['Keywords'].append(['NaN'])

                if reasons==[]:
                    reasons=self.extract_reasons(to_extract)
                if reasons:
                    self.socialconst_results['Reasons'].append(reasons)
                else:
                    self.socialconst_results['Reasons'].append(['NaN'])
                
                
                if 'economically' in row['Questionnaire']: 
                        self.socialconst_results['Type'].append('Economically Successful')
                elif 'prestigious' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Prestigious')
                elif 'special treatments' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Special Treatments')
                elif 'resources' in row['Questionnaire']:
                    self.socialconst_results['Type'].append('Resources')  
                self.socialconst_results['Group'].append(group)  

    def extract_openended(self):
        self.openended_results={'Keywords':[],'Reasons':[],'Ratings':[],'Overall_Rating':[],'Overall_Reasons':[],'Group':[]}
        for group in self.group:
            self.openended_results['Group'].append(group)
            for i, row in self.df.query("Construct=='OPENENDED' and Group==@group").iterrows():
                to_extract=[s for s in row['Answer'].split('\n\n') if s!='']
                keywords=[]
                reasons=[]
                ratings={}
                rate=[]
                if 'I am studying'in row['Questionnaire']:
                    keywords=self.extract_keywords(to_extract)
                    if keywords:
                        if type(keywords[-1])==list:
                            reasons=keywords[-1]
                            keywords=keywords[:-1]
                            self.openended_results['Reasons'].append(reasons)
                        else:
                            self.openended_results['Reasons'].append(['NaN'])
                        self.openended_results['Keywords'].append(keywords)
                    else:
                        self.openended_results['Keywords'].append(['NaN'])
                elif 'make an overall' in row['Questionnaire']:
                    rate=self.extract_overall_rating(to_extract)
                    if rate:
                        self.openended_results['Overall_Rating'].append(rate)
                    else:
                        self.openended_results['Overall_Rating'].append(['NaN'])
                    reasons=self.extract_reasons(to_extract)
                    if reasons==[]:
                        reasons=[t for t in to_extract if (not has_numbers(t))] 
                    reasons=[t for t in reasons if (not t.isdigit())]  
                    if reasons:
                        self.openended_results['Overall_Reasons'].append(reasons)
                    else:
                        self.openended_results['Overall_Reasons'].append(['NaN'])
                else:
                    ratings=self.extract_ratings(to_extract)
                    self.openended_results['Ratings'].append(ratings)

    def convert_results_to_df(self,result):
        if 'Ratings' in result.keys():
            if type(result['Ratings'][0])!=dict: 
                r=pd.DataFrame(result['Ratings'],columns=['Ratings'])
            else:
                r=pd.DataFrame(result['Ratings'])
            if 'Group' not in result.keys():
                r['Group']=self.group
        else:
            if 'Group' not in result.keys():
                r = pd.DataFrame(self.group,columns=['Group'])
        for k in result.keys():
            if k=='Ratings':
                continue
            r[k]=result[k]
        return r

    def save_results_to_df(self,outdir=None,result_to_convert=None):
        if not result_to_convert:
            result_to_convert=['openended','emotion','behavior','socialconstruct']
        if type(result_to_convert)==str:
            result_to_convert=[result_to_convert]

        for convert in result_to_convert:
            if convert=='openended':
                try:
                    self.openended_results
                except:
                    self.extract_openended()
                df = self.convert_results_to_df(self.openended_results)
            if convert=='emotion':
                try:
                    self.emotion_results
                except:
                    self.extract_emotion() 
                df = self.convert_results_to_df(self.emotion_results)
            if convert=='behavior':
                try:
                    self.behavior_results
                except:
                    self.extract_behavior() 
                df = self.convert_results_to_df(self.behavior_results)
            if convert=='socialconstruct':
                try:
                    self.socialconst_results
                except:
                    self.extract_socialconst()
                df = self.convert_results_to_df(self.socialconst_results)

            if outdir:
                df.to_csv('result/{outdir}')
                print(f"Saved to result/{outdir}")
            else:
                i=0
                base = f'processed_sscm_{self.model}_{convert}_{i}'
                while os.path.exists(f'result/{base}.csv'):
                    i+=1
                    base = f'processed_sscm_{self.model}_{convert}_{i}'
                df.to_csv(f'result/{base}.csv')
                print(f"Saved to result/{base}.csv!!")

if __name__=='__main__':
    parser:ArgumentParser = ArgumentParser()
    parser.add_argument('--model',help='Select from: [bard,text-davinci-003,gpt-3.5-turbo]')
    parser.add_argument('--file', help='Result file to extract')
    parser.add_argument('--result_to_convert',default='')
    args=parser.parse_args() 

    if args.model=='bard':
        extracter=Bard_Result(args.file)
    elif args.model=='text-davinci-003':
        extracter=Davinci_Result(args.file)
    else:
        extracter=GPT35_Result(args.file)
    
    if args.result_to_convert=='':
        extracter.save_results_to_df() 
    else:
        extracter.save_results_to_df(result_to_convert=args.result_to_convert)










            