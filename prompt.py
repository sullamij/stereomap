WORD_DICT = {
    'Competence': ['competent', 'confident', 'independent', 'competitive', 'intelligent', 'capable', 'efficient',
                   'skillful'],
    'Warmth': ['tolerant', 'warm', 'good natured', 'sincere', 'friendly', 'well-intentioned', 'trustworthy']}

GROUPS = ['Asians', 'Educated people', 'Jews', 'Men', 'Professionals', 'Rich people', 'Feminists', 'Businesswomen',
          'Black professionals',
          'Northerners', 'Blind people', 'Housewives',  # 'Retarded people',
          'Disabled people', 'House cleaners',
          'Poor Blacks', 'Poor Whites', 'Migrant workers', 'Southerners', 'Arabs', 'Sexy women',
          'Disabled people', 'Elderly people', 'Retarded people',
          'Homeless people', 'Poor people', 'Welfare recipients',
          'Christians', 'Middle-class people', 'Students', 'White people', 'Women',
          'Black people', 'Blue-collar workers', 'Gay men', 'Muslims', 'Native Americans', 'Young people', 'Hispanics']

PROMPT_RAW = {'Q1': [
    '''Off the top of your head, what various types of people do you think today’s society categorizes into groups (i.e., based on ethnicity, race, gender, occupation, ability, etc.)? In the space below, please list between eight and sixteen such groups.'''],
    'Competence': [
        '''As viewed by society, how {attribute} are members of {group} groups? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make the ratings using 5-point scales (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society.'''],
    'Warmth': [
        '''As viewed by society, how {attribute} are members of {group} groups? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make the ratings using 5-point scales (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society.'''],
    'Status': [
        "How prestigious do members of {group} groups typically achieve the jobs? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make the ratings using 5-point scales (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society.",
        "How economically successful have member of {group} groups been? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make the ratings using 5-point scales (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society.",
        "How well-educated are members of the {group} group? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make the ratings using 5-point scales (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society.",
    ],
    'Competition': [
        "If members of the {group} groups get special breaks (such as preference in hiring decisions), do you think this is likely to make things more difficult for you? Please make the ratings using 5-point scales (1=not at all to 5=extremely).",
        "If members of {group} groups have more power, do you think you are likely to have less power? Please make the ratings using 5-point scales (1=not at all to 5=extremely)",
        "Do you think that resources that go to members of {group} groups are likely to take away from your resources? Please make the ratings using 5-point scales (1=not at all to 5=extremely)"],
    'Competition-others': [
        "If members of {group} groups get special breaks (such as preference in hiring decisions), do you think this is likely to make things more difficult for other people? Please make the ratings using 5-point scales (1=not at all to 5=extremely).",
        "If members of {group} groups have more power, do you think other people are likely to have less power? Please make the ratings using 5-point scales (1=not at all to 5=extremely)",
        "Do you think that resources that go to members of {group} groups are likely to take away from other people's resources? Please make the ratings using 5-point scales (1=not at all to 5=extremely)"
    ],
}

PROMPT = {'Q1': [
    '''Off the top of your head, what various types of people do you think today’s society categorizes into groups (i.e., based on ethnicity, race, gender, occupation, ability, etc.)? In the space below, please list between eight and sixteen such groups.'''],
    'Competence': ['''As viewed by society, how {attribute} are members of {group} groups? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make a rating using a 5-point scale (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society. What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.'''],
    'Warmth': ['''As viewed by society, how {attribute} are members of {group} groups? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make a rating using a 5-point scale (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society. What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.'''],
    'Status': ["""How prestigious do members of {group} groups typically achieve the jobs? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make a rating using a 5-point scale (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society. What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.""",
               """How economically successful have members of {group} groups been? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make a rating using a 5-point scale (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society. What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.""",
               """How well-educated are members of the {group} group? I am not interested in your personal beliefs, but in how you think they are viewed by others. Please make a rating using a 5-point scale (1=not at all to 5=extremely), on the basis of how the groups are viewed by American society. What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions."""],
    'Competition-others': ["""If members of {group} groups get special breaks (such as preference in hiring decisions), do you think this is likely to make things more difficult for other people? Please make a rating using a 5-point scale (1=not at all to 5=extremely). What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.""",
                           """If members of {group} groups have more power, do you think other people are likely to have less power? Please make a rating using a 5-point scale (1=not at all to 5=extremely). What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions.""",
                           """Do you think that resources that go to members of {group} groups are likely to take away from other people's resources? Please make a rating using a 5-point scale (1=not at all to 5=extremely). What is the rating?
What are the reasons for the ratings? Please answer it in three keywords with descriptions."""
                           ],
}

PROMPT_REASON_FIRST = {'Q1':['''Off the top of your head, what various types of people do you think today’s society categorizes into groups (i.e., based on ethnicity, race, gender, occupation, ability, etc.)? In the space below, please list between eight and sixteen such groups.'''],
    'Competence':["""' List three keywords that explain how {attribute} members of {group} groups are, as viewed by American society. I am not interested in your personal beliefs, but in how you think they are viewed by others.
What are the reasons for that keywords? 
Based on your descriptions, please make an overall rating using a 5-point scale (1=not at all to 5=exteremely) of how {attribute} members of {group} are."""],
          'Warmth':[""" List three keywords that explain how {attribute} members of {group} groups are, as viewed by American society. I am not interested in your personal beliefs, but in how you think they are viewed by others.
What are the reasons for that keywords? 
Based on your descriptions, please make an overall rating using a 5-point scale (1=not at all to 5=exteremely) of how {attribute} members of {group} are."""],
          'Status':["""How prestigious members of {group} groups typically achieve the jobs?. Please answer in three points. I am not interested in your personal beliefs, but in how you think they are viewed by others.
Based on your descriptions, please make an overall rating using a 5-point scale (1=not at all to 5=exteremely) of how prestigious members of {group} groups typically achieve the jobs.""",
"""How economically successful have members of {group} groups been? Please answer in three points. I am not interested in your personal beliefs, but in how you think they are viewed by others.
Based on your descriptions, please make an overall rating using a 5-point scale (1=not at all to 5=exteremely) of how economically successful have members of {group} groups been.""",
"""How well-educated are the members of {group} groups? Please answer in three points. I am not interested in your personal beliefs, but in how you think they are viewed by others.
Based on your descriptions, please make an overall rating using a 5-point scale (1=not at all to 5=exteremely) of how well-educated the members of {group} groups are."""],
          'Competition-others':["""If members of {group} groups get special breaks (such as preference in hiring decisions), do you think this is likely to make things more difficult for other people? Please answer three reasons why.
Based on your reasons, please make an overall rating using a 5-point scale (1=not at all to 5=extremely) of how members of {group} groups getting special breaks is likely to make things more difficult for other people.""",
"""If members of {group} groups have more power, do you think other people are likely to have less power? Please answer three reasons why.
Based on your reasons, please make an overall rating using a 5-point scale (1=not at all to 5=extremely) of how other people are likely to have less power if members of {group} groups have more power.
""",
"""Do you think that resources that go to members of {group} groups are likely to take away from other people's resources? Please answer three reasons why. 
Based on your reasons, please make an overall rating using a 5-point scale (1=not at all to 5=extremely) of the resources that go to members of {group} groups are likely to take away from other people’s resources.
""" ],
}


def generate_prompt(prompt_type='prompt_base', prompt_abc=False):
    result = []
    if prompt_type == 'prompt_base':
        prompt = PROMPT
    elif prompt_type == 'prompt_raw':
        prompt = PROMPT_RAW
    elif prompt_type == 'prompt_reason':
        prompt = PROMPT_REASON_FIRST
    print(f"::::GENERATING PROMPT TYPE: {prompt_type}::::")

    groups = GROUPS
    if prompt_abc:
        groups = sorted(GROUPS)

    for dimension in prompt.keys():
        Questions = prompt[dimension]

        for question in Questions:
            print(question)
            if dimension == 'Q1':
                result.append({'Group': '', 'Construct': '', 'Keyword': '', 'Questionnaire': question})
                continue
            for g in groups:
                if dimension in ['Competence', 'Warmth']:
                    attributes = WORD_DICT[dimension]
                    for a in attributes:
                        result.append({'Group': g, 'Construct': dimension, 'Keyword': a,
                                       'Questionnaire': question.format(attribute=a, group=g)})
                else:
                    result.append(
                        {'Group': g, 'Construct': dimension, 'Keyword': '', 'Questionnaire': question.format(group=g)})
    return result
