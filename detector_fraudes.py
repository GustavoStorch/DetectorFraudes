import pandas as pd
import os

# Definir opções do pandas
pd.set_option('future.no_silent_downcasting', True)

fraud_percentage = 0

def load_data(file_path):
    #Carrega o dataset a partir de um arquivo CSV.#
    return pd.read_csv(file_path)

def count_frauds(df):
    #Conta a quantidade de acidentes fraudulentos e verdadeiros.#
    fraud_counts = df['FraudFound_P'].value_counts()
    fraudulentos = fraud_counts.get(1, 0)
    verdadeiros = fraud_counts.get(0, 0)
    return fraudulentos, verdadeiros

def most_common_model(df, fraud_status):
    #Retorna o modelo de veículo com mais acidentes, filtrando por status de fraude.#
    return df[df['FraudFound_P'] == fraud_status]['Make'].value_counts().idxmax()

def area_with_most_accidents(df):
    #Determina a área com mais acidentes (Urbano ou Rural).#
    return df['AccidentArea'].value_counts().idxmax()

def count_witnesses(df):
    #Conta a quantidade de acidentes com e sem testemunhas.#
    acidentes_com_testemunhas = df['WitnessPresent'].value_counts().get('Yes', 0)
    acidentes_sem_testemunhas = df['WitnessPresent'].value_counts().get('No', 0)
    return acidentes_com_testemunhas, acidentes_sem_testemunhas

def count_police_reports(df):
    #Conta a quantidade de acidentes com e sem relatório da polícia.#
    acidentes_com_relatorio = df['PoliceReportFiled'].value_counts().get('Yes', 0)
    acidentes_sem_relatorio = df['PoliceReportFiled'].value_counts().get('No', 0)
    return acidentes_com_relatorio, acidentes_sem_relatorio

def convert_age(df):
    #Converte a coluna 'AgeOfPolicyHolder' para valores numéricos.#
    df['AgeOfPolicyHolder'] = df['AgeOfPolicyHolder'].replace({
        '16 to 17': 16.5, '18 to 20': 19, '21 to 25': 23, '26 to 30': 28,
        '31 to 35': 33, '36 to 40': 38, '41 to 50': 45.5, '51 to 65': 58, 'over 65': 70
    }).astype(float)

def convert_supplements(df):
    #Converte a coluna 'NumberOfSuppliments' para valores numéricos.#
    df['NumberOfSuppliments'] = df['NumberOfSuppliments'].replace({
        'none': 0, '1 to 2': 1.5, '3 to 5': 4, '3 to 4': 3.5, 'more than 5': 6
    }).astype(float)

def calculate_statistics(df):
    #Calcula estatísticas gerais do dataset.#
    idade_media = df['AgeOfPolicyHolder'].mean()
    media_acoes_seguro = df['NumberOfSuppliments'].mean()
    quantidade_acima_media = df[df['NumberOfSuppliments'] > media_acoes_seguro].shape[0]
    condutores_menores_ou_igual_18 = df[df['AgeOfPolicyHolder'] <= 18].shape[0]
    return idade_media, media_acoes_seguro, quantidade_acima_media, condutores_menores_ou_igual_18

def validate_fraud_conditions(df):
    # """Valida condições para determinar se um acidente é potencialmente fraudulento e calcula a porcentagem de casos fraudulentos."""
    # Valida condições de fraude
    global fraud_percentage 

    df['FraudValidation'] = (
        (df['WitnessPresent'] == 'No') & 
        (df['PoliceReportFiled'] == 'No') &
        (df['AgeOfPolicyHolder'] != df['Age'])
    )
    
    # Calcula o número total de casos e o número de casos fraudulentos
    total_cases = len(df)
    fraudulent_cases = df['FraudValidation'].sum()
    
    # Calcula a porcentagem
    fraud_percentage = (fraudulent_cases / total_cases) * 100
    
    return fraudulent_cases


def generate_filename(base_name, extension='xlsx'):
    # #Gera um nome de arquivo único para evitar sobrescrita.#
    i = 1
    while True:
        file_name = f"{base_name}_v{i}.{extension}"
        if not os.path.exists(file_name):
            return file_name
        i += 1

def save_results(df_resultados, base_name):
    # 'Salva os resultados em um arquivo Excel.'
    output_file = generate_filename(base_name)
    df_resultados.to_excel(output_file, index=False)
    print(f"Os resultados foram salvos no arquivo: {output_file}")

def main():
    file_path = 'resources/dataSet/fraud_oracle.csv'
    df = load_data(file_path)

    # Contagem de fraudes e acidentes verdadeiros
    fraudulentos, verdadeiros = count_frauds(df)

    # Modelos de veículos mais envolvidos em acidentes
    modelo_verdadeiros = most_common_model(df, fraud_status=0)
    modelo_fraudulentos = most_common_model(df, fraud_status=1)

    # Área com mais acidentes
    area_mais_acidentes = area_with_most_accidents(df)

    # Testemunhas e relatórios policiais
    acidentes_com_testemunhas, acidentes_sem_testemunhas = count_witnesses(df)
    acidentes_com_relatorio, acidentes_sem_relatorio = count_police_reports(df)

    # Conversão de colunas e cálculo de estatísticas
    convert_age(df)
    convert_supplements(df)
    idade_media, media_acoes_seguro, quantidade_acima_media, condutores_menores_ou_igual_18 = calculate_statistics(df)

    # Validação de condições de fraude
    fraudes_validadas = validate_fraud_conditions(df)
    # Criar um DataFrame com os resultados
    resultados = {
        'Acidentes Fraudulentos': [fraudulentos],
        'Acidentes Verdadeiros': [verdadeiros],
        'Modelo com Mais Acidentes Verdadeiros': [modelo_verdadeiros],
        'Modelo com Mais Acidentes Fraudulentos': [modelo_fraudulentos],
        'Área com Mais Acidentes': [area_mais_acidentes],
        'Acidentes com Testemunhas': [acidentes_com_testemunhas],
        'Acidentes sem Testemunhas': [acidentes_sem_testemunhas],
        'Acidentes sem Relatório da Polícia': [acidentes_sem_relatorio],
        'Acidentes com Relatório da Polícia': [acidentes_com_relatorio],
        'Idade Média dos Titulares': [idade_media],
        'Média de Ações de Seguro': [media_acoes_seguro],
        'Quantidade Acima da Média de Ações de Seguro': [quantidade_acima_media],
        'Condutores Menores ou Igual a 18 Anos': [condutores_menores_ou_igual_18],
        'Fraudes Validadas': [fraudes_validadas],
        'Percentual de Fraudes': [f'{fraud_percentage:.2f}%']
    }

    df_resultados = pd.DataFrame(resultados)

    # Salvar os resultados em um arquivo Excel
    base_name = 'resources/results/resultados_acidentes'
    save_results(df_resultados, base_name)

if __name__ == "__main__":
    main()