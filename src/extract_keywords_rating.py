import pandas as pd 
import re 


rating_match=[r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+or\s+.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+to\s+.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+or\s+.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=on a 5-point scale)',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+to\s+.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=on a 5-point scale)',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)/',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=on the 5-point scale)',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=on a 5-point scale)',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=\(out of 5\))',
              r'(?<=Rating:)\s+((?<!\d|\.)\d+(?:\.\d+)?)',
              r'(?<=Rating:)((?<!\d|\.)\d+(?:\.\d+)?)',
              r'(?<=The rating).*((?<!\d|\.)\d+(?:\.\d+)?)',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=on a 5-point scale)',
              r'(?<=rate).*(?<=as).*((?<!\d|\.)\d+(?:\.\d+)?)\s(?=out of 5)',
              r'(?<=rate).*(?<=as).*((?<!\d|\.)\d+(?:\.\d+)?)/',
              r'(?<=rate).*(?<=as).*((?<!\d|\.)\d+(?:\.\d+)?)',
              r'^((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
              r'^((?<!\d|\.)\d+(?:\.\d+)?)',
              r'^((?<!\d|\.)\d+(?:\.\d+)?)/',
              r'((?<!\d|\.)\d+(?:\.\d+)?)/',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+(?=out of 5)',
              r'((?<!\d|\.)\d+(?:\.\d+)?)',
              r'(?<=The rating).*is\s+((?<!\d|\.)\d+(?:\.\d+)?)',
              r'.*((?<!\d|\.)\d+(?:\.\d+)?)\s+out of 5']

keyword_patterns={1:[r'(?<=:)\s+(.*?)\(.*?\),\s+(.*?)\(.*?\),\s+and\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\(.*?\);\s+(.*?)\(.*?\);\s+and\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\s+-.*?\;\s+(.*?)\s+-\s+.*?\;\s+and\s+(.*?)\s+-\s+.*',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+and\s+(.*?)([^.]+).',
                             r'\"(.*)\"\s\"(.*)\"\sand\s\"(.*)\"',
                             r'(?=This is).*(?<=because).*\s+(.*?),\s+(.*?),\s+and\s+(.*?)\.',
                             r'(?=This is).*(?<=due to)\s+(.*?),\s+(.*?),\s+and\s+(.*?)\.',
                             r'(?<=:)\s+(.*?)\(.*?\);\s+(.*?)\(.*?\);\s+(.*?)\(.*?\)',
                             r'(?<=The reasons).*are(.*?),\s+(.*?),\s+and\s+(.*?)\.',
                             r'(?<=:)\s+(.*?)\s+-.*?\;\s+(.*?)\s+-\s+.*?\;\s+(.*?)\s+-\s+.*'],
                  2:[r'(?<=:)\s+(.*?)\(.*?\),\s+(.*?)\(.*?\),\s+and\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\(.*?\);\s+(.*?)\(.*?\);\s+and\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\(.*?\);\s+(.*?)\(.*?\);\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\(.*?\),\s+(.*?)\(.*?\),\s+(.*?)\(.*?\)',
                             r'(?<=The reasons).*(?<=:)\s+(.*?)-.*;\s(.*?)-.*;\sand\s(.*?)\s-',
                             r'(?<=:)\s+(.*?)\s+-.*?\;\s+(.*?)\s+-\s+.*?\;\s+(.*?)\s+-\s+.*',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?)-',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+and\s+.*?([^.-:]+)',
                             r'(?<=:)\s+(.*?)-.*\.\s+(.*?)-.*\.\s+(.*?)-.*\.'
                              r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?)\s+[^.-:]',
                             r'(?<=:)\s+(.*?)-.*\.\s+(.*?)-.*\.\s+(.*?)-.*\.',
                             r'(?<=:)\s+(.*?)\s+-.*?\,\s+(.*?)\s+-\s+.*?\,\s+(.*?)\s+-\s+.*',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+.*?([^-.]+)',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?)([^.-:]+)',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?):',
                             r'(?<=:)\s+(.*?),\s+(.*?),\s+and\s+(.*?)([^.]+).',
                             r'(?<=:)\s+(.*?)\s+-.*?\;\s+(.*?)\s+-\s+.*?\;\s+and\s+(.*?)\s+-\s+.*',
                            r'(?<=:)\s+(.*?)\(.*?\);\s+(.*?)\(.*?\);\s+(.*?)\(.*?\)',
                             r'(?<=:)\s+(.*?)\(.*?\),\s+(.*?)\(.*?\),\s+(.*?)\(.*?\)',
                             r'(?<=The reasons).*are(.*?),\s+(.*?),\s+and\s+(.*?)\.',
                             r'(?<=The reasons).*(?<=:)(.*?)\s+-.*;\s+(.*?)\s+-;\s+and\s+(.*?)\s+-\s+(.*?)\.',
                              r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?):',
                              r'(?<=:)\s+(.*?),\s+(.*?),\s+(.*?).',
                             r'(?<=:)(.*?)\(.*?\),(.*?)\(.*?\)\sand\s(.*?)\(.*?\)'],
                 3:[r'(?<=:)\s+(.*?),\s+(.*?),\s+.*?([^-.]+)'],
                 4:[r'\d+.\s+(.*)\s+-',
                             r'\d+.\s+(.*):',r'Reason\s+\d+:\s+(.*?)\s+–',
                              r'Keywords:\s+(.*):',
                              r'Keywords:\s+(.*)\s+-',
                              r'(?<=Reasons:)\s+(.*?)\s+-.',
                              r'(?<=Reasons:)\s+(.*?),\s+(.*?),\s+(.*)',
                              r'(?<=Reasons:)\s+(.*?)\s+',
                              r'(.*?)\s+-.',
                              r'-(.*?):.',
                              r'(.*?):.',
                              r'\d.\s+(.*)\s+–',
                              r'\d\)\s+(.*?)-',
                              r'\d.\s+(.*?)-',
                              r'\d.\s+(.*)']}


def extract_keywords(df):
    keywords=[]

    for i, row in df.iterrows():
        if i==0:
            keywords.append(['NaN'])
            continue

        reasons_to_extract= [s for s in row['Answer'].split('\n') if s!='']

        found = False
        if len(reasons_to_extract)>3:
            reasons_to_extract = reasons_to_extract[-3:]
            search=[]
            for t in reasons_to_extract:
                for match in keyword_patterns[4]:
                    if re.findall(match,t):
                        search.append(re.findall(match,t)[0])
                        found=True
                        break

        elif len(reasons_to_extract)==1:
            for match in keyword_patterns[1]:
                if re.findall(match, reasons_to_extract[0]):
                    search= re.findall(match,reasons_to_extract[0])
                    found=True
                    break

        elif len(reasons_to_extract)==2:
            reasons_to_extract = reasons_to_extract[1:]
            #print(i,reasons_to_extract)
            for match in keyword_patterns[2]:
                if re.findall(match,reasons_to_extract[0]):
                    search=re.findall(match,reasons_to_extract[0])
                    found=True
                    break

        elif len(reasons_to_extract)==3:
            reasons_to_extract = reasons_to_extract[1]
            for match in keyword_patterns[3]:
                if re.findall(match, reasons_to_extract):
                    search=re.findall(match,reasons_to_extract)
                    found=True
                    break
        if not found:
            keywords.append(['NaN'])
            print(i,'NaN',reasons_to_extract)
            continue

        if type(search[0])==str:
            keywords.append(search)
            print(i,search)
            continue

        elif type(search[0])==tuple:
            search = [x.strip() for x in search[0] if x!='']

            if len(search)>3:
                keywords.append(['NaN'])
                print('len>3',search)
                continue

            for t,key in enumerate(search):
                if len(key.split(' '))==1:
                    continue
                else:
                    if "and" in key:
                        search[t]=key.split('and')[1].split('.')[0].strip()
                    elif '–' in key:
                        search[t]=key.split('–')[0].strip()
                    elif '-' in key:
                        search[t]=key.split('-')[0].strip()
                    elif ':'in key:
                        search[t]=key.split(':')[0].strip()
                    else:
                        print(search)

                    if len(search[t].split(' '))>4:
                        print('len(split)>1',search)
                        search=['NaN']
                        print(i,'NaN',search)
                        break
            keywords.append(search)
            print(i,search)

    return keywords

def extract_ratings(df,verbose=False):
    extracted_ratings = []
    for i, row in df.iterrows():
        if i==0:
            extracted_ratings.append(['NaN'])
            continue
        score_found=[]
        for answer in [s for s in row['Answer'].split('\n') if s!='']:
            for patt in rating_match:
                try:
                    score=re.findall(patt,answer)
                    if score!=[]:
                        #print(f"{i}:{answer}\t:{score}")
                        score_found=score
                        extracted_ratings.append(score)
                        break
                except:
                    continue
            else:
                continue # only executed if the inner loop did not break
            break # only executed if the inner loop did break

        if score_found==[]:
            if verbose:
                print(f"::::::::{i}-th NOT FOUND:::::::")
                print(row['Answer'])
            extracted_ratings.append(['NaN'])

    return extracted_ratings

def extract_keywords_gpt35(df,verbose=False):
    keywords=[]
    for i, row in df.iterrows():
        if i==0:
            keywords.append(['NaN'])
            continue

        reasons_to_extract= [s for s in row['Answer'].split('\n') if s!='']

        if len(reasons_to_extract)>3:
            search=[]
            for t in reasons_to_extract[-3:]:
                for match in keyword_patterns[4]:
                    if re.findall(match,t) and ('Rating' not in re.findall(match,t)[0]):
                        search.append(re.findall(match,t)[0])
                        found=True
                        break

            if len(search)!=3:
                search=[]
                for t in reasons_to_extract:

                    if 'Keywords' in t and len([x.strip() for x in t.split('Keywords:')[1].split(',')])==3: 
                            search=[x.strip() for x in t.split('Keywords:')[1].split(',')]
                            #assert(len(search)==3)
                            break

                    elif re.findall(r'\d/5\s+-\s+(.*)',t):
                        search.append(re.findall(r'\d/5\s+-\s+(.*)',t))

                    if len(search) !=3: 
                        for match in keyword_patterns[4]:
                            if len(search)==3:
                                break
                            
                            if re.findall(match,t) and ('Rating' not in re.findall(match,t)[0]):
                                search.append(re.findall(match,t)[0])
                                break
            if search==[] or len(search)!=3:
                search=['NaN']
                if verbose:
                    print(i,reasons_to_extract)                        
            
        elif len(reasons_to_extract)<=3:
            search=[]
            for t in reasons_to_extract:
                if 'Keywords' in t and len([x.strip() for x in t.split('Keywords:')[1].split(',')])==3:
                    search=[x.strip() for x in t.split('Keywords:')[1].split(',')]
                    break
            
            if search==[]:
                search =['NaN']
                if verbose:
                    print(i,reasons_to_extract)
        try:
            keywords.append([x.strip() for x in search])
        except:
            keywords.append(['NaN'])
    
    return keywords

def extract_keywords_bard(df,verbose=False):
    bard_keyword_patterns=[r'\*\s+\*\*(.*?):\*\*']
    keywords = [] 
    for i, row in df.iterrows():
        if "Off the top of your head," in row['Questionnaire']:
            keywords.append(['NaN'])
            continue 

        reasons_to_extract = [s for s in row['Answer'].split('\n') if s!='']
        search =[] 
        for t in reasons_to_extract:
            for match in bard_keyword_patterns:
                if re.findall(match,t):
                    search.append(re.findall(match,t)[0])
                    break
        if search:
            keywords.append(search)
        else: 
            if verbose: 
                print(i, reasons_to_extract)
            keywords.append(['NaN'])
    return keywords 

def run_extraction(input_dir,model,output_dir): 
    df = pd.read_csv(f'../result/{input_dir}',index_col=[])
    ratings=extract_ratings(df)
    assert(len(ratings)==len(df))
    df['Ratings'] = ratings
    df['Ratings'] = df['Ratings'].apply(lambda x: x[0])

    if model=='gpt-3.5-turbo':         
        keywords = extract_keywords_gpt35(df)
        assert(len(keywords)==len(df))
    
    elif model=='text-davinci-003': 
        keywords = extract_keywords(df)
        assert(len(keywords)==len(df))
    
    elif model=='bard':
        keywords = extract_keywords_bard(df)
        assert(len(keywords)==len(df))

    df['Keywords']=keywords
    df.to_csv(f'../result/{output_dir}.csv')
    print(f"Saved to {output_dir}") 
    
    return df  