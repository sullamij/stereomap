from sentence_transformers import SentenceTransformer 
import faiss
from src.analyze_results import *
from keybert import KeyBERT 
from sentence_transformers import SentenceTransformer 
import re

gpt35=retrieve_results('gpt-3.5-turbo','socialconstruct')
davinci=retrieve_results('text-davinci-003','socialconstruct')
bard=retrieve_results('Bard','socialconstruct')

gpt35=gpt35[gpt35['Reasons']!="['NaN']"]
gpt35=gpt35[~gpt35.duplicated(subset=['Reasons'],keep='first')][['Group','Reasons','Type']]

davinci=davinci[davinci['Reasons']!="['NaN']"]
davinci=davinci[~davinci.duplicated(subset=['Reasons'],keep='first')][['Group','Reasons','Type']]

bard=bard[bard['Reasons']!="['NaN']"]
bard=bard[~bard.duplicated(subset=['Reasons'],keep='first')][['Group','Reasons','Type']]

davinci=davinci.query("Type=='Economically Successful'")

bard=bard.query("Type=='Economically Successful'")

gpt35=gpt35.query("Type=='Economically Successful'")

cluster_df=get_cluster_df(model='text-davinci-003')
cluster_df['Group']=cluster_df['Group'].apply(lambda x: x.lower())
df=pd.merge(davinci, cluster_df, on='Group')

sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
kw_model = KeyBERT(model=sentence_model)

import ast 
results = [] 
for i, row in df.iterrows():
    reasons = ast.literal_eval(row['Reasons'])
    for r in reasons:
        print(r)
        group = row['Group']
        cluster = row['NCluster']
        results.extend([(r,group, cluster)])

reason_df=pd.DataFrame()
reason_df['Group'] = [result[1] for result in results]
reason_df['Cluster'] = [result[2] for result in results]
reason_df['Reason'] = [result[0] for result in results]

group_list =list(reason_df.Group.unique())
stopwords=['stereotypes','keywords','associate','stereotyped','stereotype','associated','success','successful','hindus','americans',
           'buddhist','arab','asian','welfare','recipients','bisexual','bisexuals','entrepreneurs','Asians','Arabs','Buddhists',
            'Christians', 'Muslims','Black','Indian Americans','Ivy','CEOs','Hispanics','arabs','buddhists','ceos','american',
            'asians','christians','hispanics','goths','whites','ivy','leaguers','muslim','artists','bluecollar','whitecollar','christian','hippies',
            'germans', 'atheism', 'catholic','church','drug','addiction','athlete','musician', 'blind','people'
           ] 
group_list=[g.lower() for g in group_list]

for cluster in reason_df.Cluster.unique(): 
    print(cluster)
    reasons=reason_df.query("Cluster==@cluster")   
    text=" ".join(reasons['Reason'].tolist())
    text=['they' if (re.sub(r'[^\w\s]','',t.lower()) in group_list) else re.sub(r'[^\w\s]','',t.lower()) for t in text.split(' ')]
    text=" ".join([t.strip() for t in text if t.strip() not in stopwords])
    print(kw_model.extract_keywords(text,keyphrase_ngram_range=(1,3),stop_words='english',
                                use_maxsum=True, nr_candidates=20,top_n=15))
    print(kw_model.extract_keywords(text,keyphrase_ngram_range=(1,3),stop_words='english',
                                use_mmr=True, diversity=0.7,top_n=15,))
    print(kw_model.extract_keywords(text,keyphrase_ngram_range=(1,3),stop_words='english',
                                use_mmr=True, diversity=0.2, top_n=15,))  
