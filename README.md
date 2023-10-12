# 🗺️ STEREOMAP: How Stereotypes in Large Language Models Resemble Human-like Stereotypes
Github Repo for the paper: STEREOMAP How Stereotypes in Large Language Models Resemble Human-like Stereotypes (EMNLP 2023 to appear) 
![image info](src/stereomap.png)

-----
### File Description 📃
1. Querying

`query_LLM.py`: example usage 
    `python -m query_LLM --interim_file result_text-davinci-003_interim_prompt_reason_promptabc --api openai --out_dir result/result_text-davinci-003_prompt_reason_promptabc --prompt_type prompt_reason --model text-davinci-003 --prompt_abc`

2. Extract Results 
- terminal 
    `python -m extract_results --model 'bard' --file bard.csv`

- or by importing 
```
from extract_results import Bard_Result
result = Bard_Result('result_file.csv')
result.save_results_to_df() 
```
! Note: the result parser is built post-hoc, i.e., after analyzing the response syntax given by the models. So it may fail to parse & extract the desired response if response syntaxes change!

3. Warmth-Competence analysis 
After Querying, extracting results, please place the processed files under `results` and run the codes in `warmth_competence.py` 

4. Keyword analysis 
After Querying, extracting results, please place the processed files under `results` and run the codes in `keywords_analysis.py` 

5. Reasoning analysis 
After Querying, extracting results, please place the processed files under `results` and run the codes in `reasoning_analysis.py` 

### Install 

`pip install -r requirements.txt`

For BardAPI setting and usage please refer to https://github.com/acheong08/Bard , https://github.com/dsdanielpark/Bard-API
