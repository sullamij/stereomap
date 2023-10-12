import argparse
import os
from argparse import ArgumentParser
from bardapi import Bard
#from prompt import generate_prompt
from prompt_extend import generate_prompt
import random
import time

from tqdm import tqdm
import pickle
import pandas as pd
import openai

BARD_TOKEN = '{BARD_TOKEN}'
OPENAI_API_KEY = '{OPENAI_KEY}'



def query_bard(args):
    ## For BardAPI setting and usage please refer to https://github.com/acheong08/Bard , https://github.com/dsdanielpark/Bard-API
    bard = Bard(token=BARD_TOKEN)
    if args.interim_file:
        if os.path.exists(args.interim_file):
            print('******Loading interim file******')
            with open(args.interim_file, 'rb') as f:
                result = pickle.load(f)
        else:
            result = generate_prompt(args.prompt_type,args.prompt_abc)
    else:
        ### generate prompts ###
        result = generate_prompt(args.prompt_type,args.prompt_abc)
        rand = random.randint(0, 111)
        args.interim_file = f'result_bard_interim_{rand}'
        print(f"Temporary_file will be stored to {args.interim_file}")

    for i, row in tqdm(enumerate(result)):
        if 'Answer' in row.keys():
            if 'Response Error' not in row['Answer']:
                continue
        try:
            response = bard.get_answer(row['Questionnaire'])
            if 'Response Error' in response['content']:
                print(f"Response Error --passing {i}-th instance")
                print("*********Ending Execution at {i}-th instance**********")
                print(f"****Saving interim file to {args.interim_file}")
                with open(args.interim_file, 'wb') as f:
                    pickle.dump(result, f)
                print("=========Saved!=========")
                break
            row['Answer'] = response['content']
            if response['choices']:
                for n, choice in enumerate(response['choices']):
                    row[f'Choice_{n}'] = choice['content']
            time.sleep(5)
        except:
            print(f'Exception occured !! {i}-th')
            time.sleep(20)

    with open(args.interim_file, 'wb') as f:
        pickle.dump(result,f)

    df=pd.DataFrame.from_dict(result,orient='columns')
    df.to_csv(args.out_dir)


def query_openai(args):
    openai.api_key = OPENAI_API_KEY
    print(f':::::Running {args.model}:::::')
    if args.interim_file:
        if os.path.exists(args.interim_file):
            print('******Loading interim file******')
            with open(args.interim_file, 'rb') as f:
                result = pickle.load(f)
        else:
            result =generate_prompt(args.prompt_type,args.prompt_abc,args.model)
    else:
        ### generate prompts ###
        result = generate_prompt(args.prompt_type,args.prompt_abc)
        rand = random.randint(0, 111)
        args.interim_file = f'result_{args.model}_interim_{rand}'
        print(f"Temporary_file will be stored to {args.interim_file}")

    for i, row in tqdm(enumerate(result)):
        if 'Answer' in row.keys():
            if 'Response Error' not in row['Answer']:
                continue
        if args.model in ['gpt-3.5-turbo', 'gpt-4-32k']:
            try:
                response = openai.ChatCompletion.create(
                    model=args.model,
                    messages=[
                        {'role': 'user', 'content': row['Questionnaire']}
                    ]
                )
                # print(response['choices'][0]['message']['content'])
                row['Answer'] = response['choices'][0]['message']['content']
                # print(row['Answer'])
                time.sleep(10)
            except:
                print(f'Exception occured !! {i}-th')
                with open(args.interim_file, 'wb') as f:
                    pickle.dump(result, f)
                print("=========Saved!=========")
                time.sleep(30)

        if args.model in ['text-davinci-003', 'text-curie-001']:
            try:
                response = openai.Completion.create(
                    engine=args.model, prompt=row['Questionnaire'],
                    max_tokens=800, n=1, temperature=0.5)
                row['Answer'] = response['choices'][0]['text']
                if i %101 ==0:
                    print(row['Answer'])
                    with open(args.interim_file,'wb') as f:
                        pickle.dump(result,f)
                time.sleep(5)
            except:
                print(f'Exception occured !! {i}-th')
                with open(args.interim_file, 'wb') as f:
                    pickle.dump(result, f)
                print("=========Saved!=========")
                time.sleep(30)
    with open(args.interim_file,'wb') as f:
        pickle.dump(result,f)

    df = pd.DataFrame.from_dict(result, orient='columns')
    df.to_csv(args.out_dir+'.csv')
    print("=========Saved!=========")



if __name__ == '__main__':
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('--interim_file', help='the interim file path')
    parser.add_argument('--api', default='bard', help='Select from: [bard, openai]')
    parser.add_argument('--model', default='gpt-3.5-turbo')
    parser.add_argument('--out_dir', help='Directory to store results')
    parser.add_argument('--prompt_type', default='prompt_base', help='Select from:[prompt_base, prompt_raw]')
    parser.add_argument('--prompt_abc', action='store_true', help='Sorts the GROUPS in alphabetical order')
    args = parser.parse_args()

    if args.api == 'openai':
        query_openai(args)

    elif args.api == 'bard':
        query_bard(args)
