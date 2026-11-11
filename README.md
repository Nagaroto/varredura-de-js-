# JS Path Scanner

Ferramenta desenvolvida para identificar, extrair e analisar referências a arquivos JavaScript presentes no HTML de aplicações web.

## Sobre o projeto

O JS Path Scanner realiza uma varredura no HTML previamente obtido de uma aplicação, procurando referências a arquivos JavaScript que possam estar declaradas diretamente no código ou ocultadas por codificação Base64.

O objetivo é facilitar o reconhecimento de arquivos JavaScript utilizados pela aplicação, identificando seus caminhos e permitindo mapear melhor sua estrutura de recursos.

## Funcionalidades

- **Varredura de HTML:** análise do conteúdo HTML fornecido.
- **Identificação de chamadas JavaScript:** reconhecimento de referências diretas a arquivos JS.
- **Detecção de Base64:** identificação de referências codificadas.
- **Decodificação automática:** reversão de conteúdo Base64 para recuperar as referências originais.
- **Extração de caminhos:** identificação e exibição dos caminhos encontrados.
- **Organização dos resultados:** apresentação das referências identificadas para facilitar análises posteriores.

## Fluxo de funcionamento

1. O HTML da aplicação é obtido previamente.
2. O conteúdo é submetido à ferramenta para análise.
3. São realizadas buscas por referências a arquivos JavaScript.
4. Referências codificadas em Base64 são identificadas e decodificadas.
5. Os caminhos recuperados são extraídos e apresentados nos resultados.

## Estrutura do projeto

```text
baixar_js/
├── bs/
└── py/
```

## Objetivo

Facilitar etapas de reconhecimento em aplicações web, permitindo localizar arquivos JavaScript referenciados no HTML e identificar caminhos que poderiam passar despercebidos durante uma análise manual.

## Contexto de uso

Desenvolvida para auxiliar em atividades de reconhecimento e análise de aplicações web, especialmente durante investigações de superfície de exposição e mapeamento de recursos JavaScript.

---

**JS Path Scanner** — JavaScript Reference Discovery Tool.
