import re
import pandas as pd

def ler_arquivo(file_path):
    """Lê o conteúdo de um arquivo texto."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

def extract_employee_data(text):
    """Extrai dados dos funcionários do texto fornecido (via regex)."""
    data = []
    
    service_segments = re.split(r'\nServiço\:\s*', text)
    
    for segment in service_segments:
        if not segment.strip():
            continue

        service = 'N/A'
        if 'Empr.:' in segment:
            lines = segment.strip().split('\n')
            service_line = lines[0]
            service = service_line.strip()
            emp_text = '\n'.join(lines[1:])
        else:
            emp_text = segment

        employees = re.split(r'\nEmpr\.\:', emp_text)
        
        for emp in employees:
            emp = emp.strip()
            if not emp:
                continue

            if not emp.startswith('Empr.:'):
                emp = 'Empr.:' + emp

            name_match = re.search(r'Empr\.\:\s*(\d+)\s*(.*?)\s*Situação', emp)
            id_match = re.search(r'Empr\.\:\s*(\d+)', emp)
            vinculo_match = re.search(r'Vínculo\:\s*(.*?)\s*CC\:', emp)

            if name_match and id_match and vinculo_match:
                name = name_match.group(2).strip()
                emp_id = id_match.group(1).strip()
                vinculo = vinculo_match.group(1).strip()

                lines = emp.strip().split('\n')
                pattern = re.compile(r'(\d+)\s+(.+?)\s+([\d\:\,]+)\s+([\d\.\,\-]+)\s+([PD])')
                
                for line in lines:
                    matches = re.findall(pattern, line)
                    
                    for match in matches:
                        codigo, descricao, quantidade, valor, tipo = match
                        if tipo == 'P':
                            data.append({
                                'NOME FUNCIONARIO': name,
                                'ID (MATRICULA)': emp_id,
                                'VINCULO': vinculo,
                                'RUBRICA': descricao.strip(),
                                'VALOR DA RUBRICA': valor.strip(),
                                'SERVICO': service
                            })
            else:
                continue

    return data

def salvar_arquivo(df, output_destination):
    """Salva o DataFrame em um arquivo Excel no caminho especificado ou em um buffer de memória."""
    # Cria uma cópia do DataFrame para evitar modificar o original
    df_copy = df.copy()
    df_copy['VALOR DA RUBRICA'] = df_copy['VALOR DA RUBRICA'].str.replace('.', '', regex=False)
    df_copy['VALOR DA RUBRICA'] = df_copy['VALOR DA RUBRICA'].str.replace(',', '.', regex=False)
    df_copy['VALOR DA RUBRICA'] = pd.to_numeric(df_copy['VALOR DA RUBRICA'], errors='coerce')

    try:
        if isinstance(output_destination, str):
            # Se for um caminho de arquivo, salva no disco
            df_copy.to_excel(output_destination, index=False)
            print(f"Arquivo Excel salvo com sucesso em: {output_destination}")
        else:
            # Se for um objeto BytesIO, salva no buffer
            with pd.ExcelWriter(output_destination, engine='xlsxwriter') as writer:
                df_copy.to_excel(writer, index=False, sheet_name='Dados Funcionarios')
            print("DataFrame salvo em buffer de memória.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")