import pdfplumber
import os

def processar_pagina(words):
    """Organiza as 'palavras' em linhas mantendo a estrutura original (pdf -> texto)."""
    if not words:
        return []
    
    # Ordena por coordenadas Y (top) e X (x0)
    palavras_ordenadas = sorted(words, key=lambda x: (x['top'], x['x0']))
    
    linhas = []
    linha_atual = []
    y_anterior = palavras_ordenadas[0]['top']
    
    for palavra in palavras_ordenadas:
        # Tolerância de 5 pontos para considerar mesma linha
        if abs(palavra['top'] - y_anterior) < 5:
            linha_atual.append(palavra['text'])
        else:
            linhas.append(' '.join(linha_atual))
            linha_atual = [palavra['text']]
            y_anterior = palavra['top']
    
    if linha_atual:
        linhas.append(' '.join(linha_atual))
    
    return linhas

def extrair_servicos_e_funcionarios(pdf_path):
    """
    Extrai blocos de serviço e, dentro deles, blocos de funcionários.
    """
    servicos = []
    servico_atual_linhas = []
    funcionarios_do_servico = []
    capturando_servico = False
    capturando_funcionario = False
    bloco_funcionario_atual = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=0.5, y_tolerance=0.5)
            linhas = processar_pagina(words)

            for linha in linhas:
                if "Serviço:" in linha:
                    if capturando_servico:
                        if capturando_funcionario and bloco_funcionario_atual:
                            funcionarios_do_servico.append("\n".join(bloco_funcionario_atual))
                        
                        servico_completo = servico_atual_linhas + funcionarios_do_servico
                        servicos.append("\n".join(servico_completo))

                    servico_atual_linhas = [linha]
                    funcionarios_do_servico = []
                    capturando_servico = True
                    capturando_funcionario = False
                    bloco_funcionario_atual = []
                    continue
                
                if capturando_servico:
                    if "Empr.:" in linha:
                        if capturando_funcionario and bloco_funcionario_atual:
                            funcionarios_do_servico.append("\n".join(bloco_funcionario_atual))
                        
                        capturando_funcionario = True
                        bloco_funcionario_atual = [linha]
                        continue
                    
                    if capturando_funcionario:
                        bloco_funcionario_atual.append(linha)
                        if "Base IRRF:" in linha:
                            try:
                                prefixo, sufixo = linha.split("Base IRRF:", 1)
                                bloco_funcionario_atual[-1] = prefixo.strip()
                                valor_irrf = sufixo.split()[0] if sufixo.strip() else ''
                                bloco_funcionario_atual.append(f"Base IRRF: {valor_irrf}")
                            except ValueError:
                                pass
                            
                            funcionarios_do_servico.append("\n".join(bloco_funcionario_atual))
                            bloco_funcionario_atual = []
                            capturando_funcionario = False

    if capturando_servico:
        if capturando_funcionario and bloco_funcionario_atual:
            funcionarios_do_servico.append("\n".join(bloco_funcionario_atual))
        
        servico_completo = servico_atual_linhas + funcionarios_do_servico
        servicos.append("\n".join(servico_completo))
    
    return servicos

def gerar_txt_de_pdf(pdf_path, txt_path):
    """
    Função auxiliar que extrai do PDF e salva em um arquivo TXT.
    """
    blocos_servicos = extrair_servicos_e_funcionarios(pdf_path)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocos_servicos))
    return txt_path