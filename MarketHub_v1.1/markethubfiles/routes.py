from flask import redirect, url_for, flash, render_template, request, make_response, session
from markethubfiles import app
from markethubfiles.forms import FormLogin, SearchForm
import pandas as pd
import psycopg2
from flask_wtf.csrf import generate_csrf
import pdfkit
import os

def exist_prec(chave_nfe):
    # Conectar ao banco PostgreSQL
    postgres_conn = psycopg2.connect(
        "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
    )
    postgres_cursor = postgres_conn.cursor()

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(f'''
        SELECT *
        FROM output_precificacao
        WHERE chave_nfe = '{chave_nfe}'
         ''')
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['id', 'descricao', 'ean_tributado', 'sale_type', 'quantidade', 'valor_total', 'valor_desconto',
               'v_icms_st', 'valor_ipi', 'preco_compra', 'preco_min', 'qtd_emb', 'confirmada', 'preco_calculado', 'fator_conversao',
               'chave_nfe']
    df = pd.DataFrame(dados, columns=colunas)
    df = df.drop(columns='id')
    print(df.columns)

    return df

def verificar_credenciais(email, senha):
    # Conectar ao banco PostgreSQL
    postgres_conn = psycopg2.connect(
        "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
    )
    postgres_cursor = postgres_conn.cursor()

    # Executar a consulta para verificar as credenciais
    postgres_cursor.execute(f'''
        SELECT id, user_name, email
        FROM users
        WHERE email = %s AND password = %s
    ''', (email, senha))

    # Obter o resultado da consulta
    usuario_data = postgres_cursor.fetchone()

    # Fechar a conexão com o banco de dados
    postgres_cursor.close()
    postgres_conn.close()

    return usuario_data  # Retorna os dados do usuário, se encontrados, ou None se as credenciais forem inválidas

# Função para buscar dados no banco de dados
def buscar_dados(codigo):
    # Conectar ao banco PostgreSQL
    postgres_conn = psycopg2.connect(
        "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
    )
    postgres_cursor = postgres_conn.cursor()

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(f'''
        SELECT
            CHAVE_NFE,
            DESCRICAO,
            EAN_trib,
            SALE_TYPE,
            QUANTIDADE,
            VALOR_TOTAL,
            VALOR_DESCONTO,
            V_ICMS_ST,
            VALOR_IPI,
            PRECO_COMPRA,
            PRECO_MIN,
            QTD_EMBALAGEM
        FROM precificacao
        WHERE CHAVE_NFE = '{codigo}'
         ''')
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['CHAVE_NFE','DESCRICAO', 'EAN_trib', 'SALE_TYPE', 'QUANTIDADE', 'VALOR_TOTAL', 'VALOR_DESCONTO', 'V_ICMS_ST',
               'VALOR_IPI', 'PRECO_COMPRA', 'PRECO_MIN', 'QTD_EMBALAGEM']
    df = pd.DataFrame(dados, columns=colunas)

    # Fazendo alguns tratamentos no DF
    df['VALOR_IPI'] = df['VALOR_IPI'].replace('None', 0)
    df['PRECO_COMPRA'] = df['PRECO_COMPRA'].replace('None', 0)
    df['PRECO_MIN'] = df['PRECO_MIN'].replace('None', 0)
    df['QTD_EMBALAGEM'] = df['QTD_EMBALAGEM'].replace('None', 0)
    df['VALOR_DESCONTO'] = df['VALOR_DESCONTO'].replace('None', 0)
    df['V_ICMS_ST'] = df['V_ICMS_ST'].replace('None', 0)
    df['V_ICMS_ST'] = df['V_ICMS_ST'].astype(float)
    df['VALOR_IPI'] = df['VALOR_IPI'].replace('None', 0)
    df['VALOR_IPI'] = df['VALOR_IPI'].astype(float)
    df['icms_st/ipi'] = df['V_ICMS_ST'] + df['VALOR_IPI']

    # Inicializa a coluna 'confirmada' como False
    df['confirmada'] = False

    colunas = ['CHAVE_NFE','DESCRICAO', 'EAN_trib', 'SALE_TYPE', 'QUANTIDADE', 'VALOR_TOTAL', 'VALOR_DESCONTO'
               ,'icms_st/ipi' ,'PRECO_COMPRA', 'PRECO_MIN', 'QTD_EMBALAGEM']

    ## adicionando
    #preço ultima compra
    #preço atual do produto no sistema

    postgres_cursor.execute('''
        SELECT * FROM precos_api
    ''')
    dados = postgres_cursor.fetchall()
    colunas_2 = ['id','date_insert', 'sku', 'ean', 'preco_ultima_compra',
                 'preco_venda']
    df_2 = pd.DataFrame(dados, columns=colunas_2)

    rename = {
        'CHAVE_NFE': 'Chave',
        'DESCRICAO': 'Produto',
        'EAN_trib': 'EAN',
        'SALE_TYPE': 'Embalagem',
        'QUANTIDADE': 'Quantidade',
        'VALOR_TOTAL': 'Valor total',
        'VALOR_DESCONTO': 'Valor desconto',
        'PRECO_COMPRA': 'Preço compra',
        'PRECO_MIN': 'Preço mínimo',
        'QTD_EMBALAGEM': 'Qtd embalagem'
    }

    df = df[colunas]
    df = df.rename(columns=rename)

    df_merge = pd.merge(df, df_2, how='left', left_on= 'EAN', right_on='ean')
    df_merge = df_merge.drop(columns=['id','date_insert','sku','ean'])
    df_merge['preco_ultima_compra'] = df_merge['preco_ultima_compra'].fillna(0)
    df_merge['preco_venda'] = df_merge['preco_venda'].fillna(0)
    rename_2 = {
        'preco_ultima_compra': 'Última compra',
        'preco_venda': 'Venda Atual'
    }
    df_merge = df_merge.rename(columns=rename_2)

    print(f'DataFrame com os dados da consulta: {df_merge}')

    return df_merge

def buscar_dados_impression():
    # Conectar ao banco PostgreSQL
    postgres_conn = psycopg2.connect(
        "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
    )
    postgres_cursor = postgres_conn.cursor()

    dataframe = session.get('dataframe')
    chave_nfe = dataframe['Chave'][0]

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(f'''
        SELECT
            chave_nfe,
            descricao,
            ean_tributado,
            sale_type,
            quantidade,
            valor_total,
            valor_desconto,
            v_icms_st,
            valor_ipi,
            preco_compra,
            preco_min,
            qtd_emb,
            preco_calculado,
            fator_conversao
            
        FROM output_precificacao
        WHERE chave_nfe = '{chave_nfe}'
         ''')
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['chave_nfe', 'descricao', 'ean_tributado', 'sale_type', 'quantidade', 'valor_total', 'valor_desconto', 'v_icms_st',
                'valor_ipi', 'preco_compra', 'preco_min', 'qtd_emb', 'preco_calculado', 'fator_conversao']
    df = pd.DataFrame(dados, columns=colunas)

    rename = {
        'descricao': 'Produto',
        'ean_tributado': 'EAN',
        'sale_type': 'Embalagem',
        'quantidade': 'Quantidade',
        'valor_total': 'Valor total',
        'valor_desconto': 'Valor desconto',
        'preco_compra': 'Preço compra',
        'preco_min': 'Preço mínimo',
        'qtd_emb': 'Qtd embalagem',
        'preco_calculado': 'Preço Venda'
    }

    df = df.rename(columns=rename)

    ## adicionando informações de preço de venda atual e preço de última compra

    postgres_cursor.execute('''
            SELECT * FROM precos_api
        ''')
    dados = postgres_cursor.fetchall()
    colunas_2 = ['id', 'date_insert', 'sku', 'ean', 'preco_ultima_compra',
                 'preco_venda']
    df_2 = pd.DataFrame(dados, columns=colunas_2)

    df_merge = pd.merge(df, df_2, how='left', left_on='EAN', right_on='ean')
    df_merge = df_merge.drop(columns=['id', 'date_insert', 'sku', 'ean'])
    df_merge['preco_ultima_compra'] = df_merge['preco_ultima_compra'].fillna(0)
    df_merge['preco_venda'] = df_merge['preco_venda'].fillna(0)
    rename_2 = {
        'preco_ultima_compra': 'Última compra',
        'preco_venda': 'Venda Atual'
    }
    df_merge = df_merge.rename(columns=rename_2)

    print(f'DataFrame com os dados da consulta: {df_merge}')

    return df_merge

def infos_aux():
    # Conectar ao banco PostgreSQL
    postgres_conn = psycopg2.connect(
        "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
    )
    postgres_cursor = postgres_conn.cursor()
    dataframe = session.get('dataframe')
    print(dataframe.columns)
    chave_nfe = dataframe['Chave'][0]

    ## query report notas fiscais

    report_notas_fiscais = f'''
        SELECT
            id,
            data_registro,
            id_uniplus,
            data_emissao,
            fornecedor,
            CPNJ_CPF,
            valor,
            vencimento,
            situacao,
            manifestacao,
            status,
            chave,
            data_inclusao,
            processed
        FROM report_uniplus_notas_fiscais
        WHERE chave = '{chave_nfe}'
    '''

    report_deep_nfes = f'''
        SELECT
            id,
            data_registro,
            chave_nfe,
            CPNJ_FORNECEDOR,
            NOME_FORNECEDOR,
            NOME_FANTASIA_FORNECEDOR,
            CEP_FORNECEDOR,
            CNPJ_CLIENTE,
            VALOR_TOTAL,
            VALOR_DESCONTO,
            VALOR_LIQUIDO,
            VALOR_PAGAMENTO,
            DATA_VENCIMENTO_DUP,
            VALOR_DUPLICADA
        FROM nfes_informations
        WHERE chave_nfe = '{chave_nfe}'
    '''

    reg_conferencia_notas_fiscais = f'''
        SELECT
            id_table,
            data_registro,
            id,
            chave,
            foto_da_nota_fiscal_url,
            foto_do_canhoto_url,
            processed,
            quem_recebeu_a_mercadoria,
            date
        FROM conferencia_notas
        WHERE Chave = '{chave_nfe}'
    '''

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(report_notas_fiscais)
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['id',
    'data_registro',
    'id_uniplus',
    'data_emissao',
    'fornecedor',
    'CPNJ_CPF',
    'valor',
    'vencimento',
    'situacao',
    'manifestacao',
    'status',
    'chave',
    'data_inclusao',
    'processed']
    df_report_notas_fiscais = pd.DataFrame(dados, columns=colunas)
    print(df_report_notas_fiscais)

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(report_deep_nfes)
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['id',
    'data_registro',
    'chave_nfe',
    'CPNJ_FORNECEDOR',
    'NOME_FORNECEDOR',
    'NOME_FANTASIA_FORNECEDOR',
    'CEP_FORNECEDOR',
    'CNPJ_CLIENTE',
    'VALOR_TOTAL',
    'VALOR_DESCONTO',
    'VALOR_LIQUIDO',
    'VALOR_PAGAMENTO',
    'DATA_VENCIMENTO_DUP',
    'VALOR_DUPLICADA']
    df_report_deep_nfes = pd.DataFrame(dados, columns=colunas)
    print(df_report_deep_nfes)

    # Faz a consulta no banco para o código fornecido
    postgres_cursor.execute(reg_conferencia_notas_fiscais)
    # Fetchall retorna uma lista de tuplas, vamos converter isso em um DataFrame
    dados = postgres_cursor.fetchall()
    colunas = ['id_table',
    'data_registro',
    'ID',
    'Chave',
    'Foto_da_nota_fiscal_URL',
    'Foto_do_canhoto_URL',
    'processed',
    'quem_recebeu_a_mercadoria',
    'date']
    df_reg_conferencia_notas_fiscais = pd.DataFrame(dados, columns=colunas)
    print(df_reg_conferencia_notas_fiscais)

    return df_report_notas_fiscais, df_report_deep_nfes, df_reg_conferencia_notas_fiscais

@app.route('/confirmar_operacao', methods=['POST'])
def confirmar_operacao():
    confirmadas = request.form.getlist('confirmar')  # Lista de índices de linhas confirmadas
    codigo = request.form['codigo']

    # Recupera o DataFrame da sessão
    df = session.get('dataframe')

    if df is not None:
        for index in confirmadas:
            # Verifica se os campos de Preço Venda e Fator Correto estão preenchidos e não são zero
            preco = request.form.get(f'preco_{index}')
            fator = request.form.get(f'fator_{index}')

            print(preco)
            print(fator)

            if preco.strip() == '' or fator.strip() == '':
                flash('Por favor, preencha todos os campos de Preço Venda e Fator Correto com valores não nulos', 'warning')
                return redirect(url_for('precificacao'))

            preco = str(preco).replace(',', '.')
            preco = float(preco)
            print(preco)
            fator = str(fator).replace(',', '.')
            fator = float(fator)
            print(fator)

            if float(preco) == 0 or float(fator) == 0:
                flash('Por favor, preencha todos os campos de Preço Calculado e Fator Correto com valores maiores que zero.', 'warning')
                return redirect(url_for('precificacao'))

            # Altera o status da linha no DataFrame
            df.at[int(index), 'confirmada'] = True
            # Atualiza os valores de "Preço Venda" e "Fator Correto" no DataFrame
            df.at[int(index), 'Preço Venda'] = preco
            df.at[int(index), 'Fator Correto'] = fator

        # Verifica se todas as operações foram confirmadas
        operacao_confirmada = all(df['confirmada'])
        print(operacao_confirmada)

        # Atualiza o DataFrame na sessão
        session['dataframe'] = df

        # Renderiza novamente a página de precificação com as alterações feitas
        form = SearchForm(request.form)
        return render_template('precificacao.html', form=form, dataframe=df, codigo=codigo, operacao_confirmada=operacao_confirmada)
    else:
        # Se o DataFrame não estiver na sessão, redireciona para a página de precificação
        return redirect(url_for('precificacao'))

@app.route('/imprimir_espelho_nota_fiscal', methods=['POST'])
def imprimir_espelho_nota_fiscal():
    df = buscar_dados_impression()
    df['Valor total'] = df['Valor total'].astype(float)
    valor_total = round(df['Valor total'].sum(), 2)
    df['Valor desconto'] = df['Valor desconto'].replace('None', 0)
    df['Valor desconto'] = df['Valor desconto'].astype(float)
    valor_desconto = round(df['Valor desconto'].sum(), 2)
    chave_nfe = df['chave_nfe'][0]
    df = df.drop(columns='chave_nfe')

    print(df.columns)

    df_report_notas_fiscais, df_report_deep_nfes, df_reg_conferencia_notas_fiscais = infos_aux()

    fornecedor = df_report_notas_fiscais['fornecedor'][0]
    print(fornecedor)
    data_hora_confe = df_reg_conferencia_notas_fiscais['date'][0]
    print(data_hora_confe)
    responsavel_confe = df_reg_conferencia_notas_fiscais['quem_recebeu_a_mercadoria'][0]
    print(responsavel_confe)
    data_emissao = df_report_notas_fiscais['data_emissao'][0]
    print(data_emissao)
    cnpj_cliente = df_report_deep_nfes['CNPJ_CLIENTE'][0]
    print(cnpj_cliente)

    # Renderiza o template para gerar o HTML
    rendered_html = render_template('report.html', dataframe=df, valor_total=valor_total
                                    , chave_nfe = chave_nfe, fornecedor=fornecedor, data_hora_confe = data_hora_confe
                                    ,responsavel_confe = responsavel_confe, data_emissao = data_emissao,
                                    cnpj_cliente = cnpj_cliente, valor_desconto = valor_desconto)

    # Configurações para o PDF
    pdf_options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '0.2cm',  # Margem superior de 0.02cm
        'margin-right': '0.02cm',  # Margem direita de 0.02cm
        'margin-bottom': '0.2cm',  # Margem inferior de 0.02cm
        'margin-left': '0.02cm'  # Margem esquerda de 0.02cm
    }

    wkhtmltopdf_path = os.path.join(os.path.dirname(__file__), 'wkhtmltopdf', 'bin',
                                    'wkhtmltopdf.exe')
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Converte o HTML em PDF
    pdf = pdfkit.from_string(rendered_html, False, options=pdf_options, configuration=config)

    # Cria uma resposta para o navegador
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=espelho_nota_fiscal.pdf'

    return response

@app.route('/finalizar_precificacao', methods=['POST'])
def finalizar_precificacao():
    dataframe = session.get('dataframe')
    print(dataframe.columns)

    if dataframe is not None:
        # Conectar ao banco de dados
        postgres_conn = psycopg2.connect(
            "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
        )
        with postgres_conn.cursor() as cursor:
            chave_nfe = dataframe['Chave'].iloc[0]  # Obter o valor da chave da primeira linha
            cursor.execute("DELETE FROM output_precificacao WHERE chave_nfe = %s", (chave_nfe,))

            # Iterar sobre as linhas do DataFrame e inserir os dados no banco de dados
            for index, row in dataframe.iterrows():
                data_tuple = (
                    row['Produto'], row['EAN'], row['Embalagem'], row['Quantidade'], row['Valor total'],
                    row['Valor desconto'], row['icms_st/ipi'], row['Preço compra'], row['Preço mínimo'],
                    row['Qtd embalagem'], row['confirmada'], row['Preço Venda'], row['Fator Correto'], chave_nfe
                )
                cursor.execute("""
                    INSERT INTO output_precificacao (
                        DESCRICAO, ean_tributado, SALE_TYPE, QUANTIDADE, VALOR_TOTAL, VALOR_DESCONTO,
                        V_ICMS_ST, VALOR_IPI, PRECO_COMPRA, PRECO_MIN, qtd_emb, confirmada, preco_calculado, fator_conversao, CHAVE_NFE
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s)
                """, data_tuple)

                print(index)

        postgres_conn.commit()
        postgres_conn.close()

        flash('Precificação finalizada com sucesso!', 'success')
        return redirect(url_for('sucesso'))
    else:
        flash('Não foi possível finalizar a precificação, pois o DataFrame está vazio.', 'error')
        return redirect(url_for('precificacao'))

# Rota inicial
@app.route('/')
def home():
    if 'usuario_id' not in session:
        # Redirecionar para a página de login se o usuário não estiver autenticado
        return redirect(url_for('login'))

    return render_template('home.html')

@app.route('/precificacao', methods=['GET', 'POST'])
def precificacao():
    if 'usuario_id' not in session:
        # Redirecionar para a página de login se o usuário não estiver autenticado
        return redirect(url_for('login'))

    form = SearchForm(request.form)
    codigo = None
    operacao_confirmada = False

    if request.method == 'POST' and form.validate():
        codigo = form.search.data
        ## se o código buscado já existe na base de output ele deve pular todas as etapas de tratamento rendereizar
        ### o output

        df_validate = exist_prec(codigo)
        print(df_validate)

        if not df_validate.empty:
            postgres_conn = psycopg2.connect(
                "postgresql://postgres:G1CG2B*6d6GEDdABGcf--dA5cb*5bEf6@monorail.proxy.rlwy.net:48186/railway"
            )
            postgres_cursor = postgres_conn.cursor()
            # Fazendo alguns tratamentos no DF
            df_validate['valor_ipi'] = df_validate['valor_ipi'].replace('None', 0)
            df_validate['preco_compra'] = df_validate['preco_compra'].replace('None', 0)
            df_validate['preco_min'] = df_validate['preco_min'].replace('None', 0)
            df_validate['qtd_emb'] = df_validate['qtd_emb'].replace('None', 0)
            df_validate['valor_desconto'] = df_validate['valor_desconto'].replace('None', 0)
            df_validate['v_icms_st'] = df_validate['v_icms_st'].replace('None', 0)
            df_validate['v_icms_st'] = df_validate['v_icms_st'].astype(float)
            df_validate['valor_ipi'] = df_validate['valor_ipi'].astype(float)
            df_validate['icms_st/ipi'] = df_validate['v_icms_st'] + df_validate['valor_ipi']

            colunas = ['chave_nfe', 'descricao', 'ean_tributado', 'sale_type', 'quantidade', 'valor_total', 'valor_desconto'
                , 'icms_st/ipi', 'preco_compra', 'preco_min', 'qtd_emb', 'confirmada' ,'preco_calculado', 'fator_conversao']

            ## adicionando
            # preço ultima compra
            # preço atual do produto no sistema

            postgres_cursor.execute('''
                SELECT * FROM precos_api
            ''')
            dados = postgres_cursor.fetchall()
            colunas_2 = ['id', 'date_insert', 'sku', 'ean', 'preco_ultima_compra',
                         'preco_venda']
            df_2 = pd.DataFrame(dados, columns=colunas_2)

            rename = {
                'chave_nfe': 'Chave',
                'descricao': 'Produto',
                'ean_tributado': 'EAN',
                'sale_type': 'Embalagem',
                'quantidade': 'Quantidade',
                'valor_total': 'Valor total',
                'valor_desconto': 'Valor desconto',
                'preco_compra': 'Preço compra',
                'preco_min': 'Preço mínimo',
                'qtd_emb': 'Qtd embalagem',
                'preco_calculado':'Preço Venda',
                'fator_conversao': 'Fator Correto'
            }

            df_validate = df_validate[colunas]
            df_validate = df_validate.rename(columns=rename)

            df_merge = pd.merge(df_validate, df_2, how='left', left_on='EAN', right_on='ean')
            df_merge = df_merge.drop(columns=['id', 'date_insert', 'sku', 'ean'])
            df_merge['preco_ultima_compra'] = df_merge['preco_ultima_compra'].fillna(0)
            df_merge['preco_venda'] = df_merge['preco_venda'].fillna(0)
            rename_2 = {
                'preco_ultima_compra': 'Última compra',
                'preco_venda': 'Venda Atual'
            }
            df = df_merge.rename(columns=rename_2)
            # Armazena o DataFrame na sessão do usuário
            session['dataframe'] = df
            session['codigo'] = codigo

        else:
            # Conectar ao banco PostgreSQL
            df = buscar_dados(codigo)  # Busca dados no banco com base no código

            # Adicionando a coluna 'confirmada' ao DataFrame
            df['confirmada'] = False

            # Armazena o DataFrame na sessão do usuário
            session['dataframe'] = df
            session['codigo'] = codigo

        # Atualiza os valores do DataFrame com os dados do formulário
        for index, row in df.iterrows():
            preco = request.form.get(f'preco_{index}')  # Obtém o valor do campo Preço Calculado
            fator = request.form.get(f'fator_{index}')  # Obtém o valor do campo Fator Correto

            print(preco)

            # Verifica se preco e fator não são None
            if preco is not None and fator is not None:
                # Verifica se os campos Preço Calculado e Fator Correto estão vazios
                if preco.strip() == '' or fator.strip() == '':
                    flash('Por favor, preencha todos os campos de Preço Calculado e Fator Correto.', 'warning')
                    continue  # Se algum dos campos estiver vazio, passa para a próxima iteração

                # Atualiza os valores no DataFrame
                df.at[index, 'Preço Venda'] = preco
                df.at[index, 'Fator Correto'] = fator

    # Recupera o DataFrame da sessão, se existir
    dataframe = session.get('dataframe')
    codigo = session.get('codigo')

    # Verifica se há uma mensagem de erro no flash
    error_message = None
    if '_flashes' in session:
        flashes = session['_flashes']
        for flash_message in flashes:
            if flash_message[0] == 'message' and flash_message[1] == 'warning':
                error_message = flash_message[2]
                break

    # Renderiza a página de precificação com os dados atualizados e a mensagem de erro, se houver
    print(dataframe)
    return render_template('precificacao.html', form=form, dataframe=dataframe, codigo=codigo,
                           operacao_confirmada=operacao_confirmada, error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        email = form_login.email.data
        senha = form_login.senha.data

        # Verificar as credenciais de login
        usuario_data = verificar_credenciais(email, senha)

        if usuario_data:
            # Cria uma sessão de usuário
            session['usuario_id'] = usuario_data[0]  # A primeira posição contém o ID do usuário
            flash(f'Login feito com sucesso no e-mail: {email}', 'alert-success')
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'alert-danger')

    return render_template('login.html', form_login=form_login)

@app.route('/logout')
def logout():
    # Limpa a sessão do usuário
    session.clear()
    # Redireciona para a página inicial ou para onde desejar após o logout
    return redirect(url_for('home'))

@app.route('/sucesso')
def sucesso():
    df = buscar_dados_impression() # Suponho que você tenha uma função para buscar os dados
    df = df.drop(columns='chave_nfe')
    print(df.columns)
    return render_template('pagina_de_sucesso.html', csrf_token=generate_csrf(), dataframe=df)



## acho que vou tirar essas informações:
#   Preço compra	Preço mínimo	Qtd embalagem

