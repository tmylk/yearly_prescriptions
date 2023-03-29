import pandas as pd


def get_antibac_prescription_data():
    return  "5.1: Antibacterial drugs",  "https://openprescribing.net/bnf/0501/", "bnf_section_code = '0501'", 'spending-0501.csv',

def get_penicillins_prescription_data():
    return "5.1.1: Penicillins", 'https://openprescribing.net/bnf/050101/',  "bnf_subsection_code = '050101'",'spending-050101.csv'

def get_amoxicillin_prescription_data():
    return "Amoxicillin (0501013B0)",  'https://openprescribing.net/chemical/0501013B0/', "bnf_code like '0501013B0%%'",  'spending-0501013B0.csv'

def get_antifungal_prescription_data():
    return "5.2: Antifungal drugs",  'https://openprescribing.net/bnf/0502/', "bnf_section_code = '0502'", 'spending-0502.csv',

def get_infection_data():
    return "5: Infections",  'https://openprescribing.net/bnf/05/',  "bnf_chapter_code = '05'", 'spending-05.csv',

def exclude_strep_a_meds():
    # the threshold for prescription was lowered in Dec 2022 -Feb 2023 by a temporary Strep A guidance https://www.nice.org.uk/guidance/ng84
    # Phenoxymethylpenicillin 0501011P0, Clarithromycin 0501050B0, Erythromycin 0501050C0 
    return " AND NOT (bnf_code like '0501011P0%%' or bnf_code like '0501050B0%%' or bnf_code like '0501050C0%%' )"

def exclude_tablets_capsule_include_lqd():
    # kids and people who can't chew
    # remove:

    # “ cap “, “ tab “, “capsule”, “tablet”

    # include:

    # “ susp “, “suspension”, “drop”, “solution”, “ soln “, “{digit}ml ”

    return " AND bnf_name regexp '.*(?: susp |suspension|drop|solution| soln |(\\d.)ml).*' AND NOT bnf_name regexp '.*(?: cap | tab | capsule|tablet).*' "


def graphs_excl_strep_a():
    for g in [get_infection_data,  get_antibac_prescription_data, get_penicillins_prescription_data, ]:
        name, url, condition, filename = g()
        name_excl_strep_a = name + " (Excl Strep A: Phenoxymethylpenicillin, Clarithromycin, Erythromycin)"
        filename_excl_strep_a = "exsa_"+filename
        condition_excl_strep_a = condition + exclude_strep_a_meds()
        
        yield name_excl_strep_a, "", condition_excl_strep_a, filename_excl_strep_a



def get_graphs_all_formulations():
    graphs_incl_strep_a = [ g() for g in [get_infection_data,  get_antibac_prescription_data, get_penicillins_prescription_data, get_amoxicillin_prescription_data, get_antifungal_prescription_data,]]
    return list(graphs_excl_strep_a()) + graphs_incl_strep_a

def get_graphs_only_liquid():
    for name, url, condition, filename in get_graphs_all_formulations():
        yield name + (" Only liquid."), "", condition + exclude_tablets_capsule_include_lqd(), "lqd_"+filename 

def get_graphs():
    return get_graphs_all_formulations() + list(get_graphs_only_liquid())

def export_prescription_data(filename):

    # select 

    df  = pd.read_csv(f'data/{filename}')
    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df.date = pd.to_datetime(df.date)
    df = df.set_index('date')

    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['months'] = pd.CategoricalIndex(df.index.strftime('%b'), ordered=True, categories=c)
    df['years'] = df.index.year
    df_pivoted = df.pivot(index='months', columns='years',values='items')
    return df_pivoted


def get_prescription_data(filename):

    df  = pd.read_csv(f'data/{filename}')
    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df.date = pd.to_datetime(df.date)
    df = df.set_index('date')

    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['months'] = pd.CategoricalIndex(df.index.strftime('%b'), ordered=True, categories=c)
    df['years'] = df.index.year
    df_pivoted = df.pivot(index='months', columns='years',values='ItemsPer1000')
    return df_pivoted
