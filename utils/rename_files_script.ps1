
# Definir o caminho da pasta (altere conforme necessário)
$pastaOrigem = Get-Location

# Verificar se a pasta existe
if (!(Test-Path $pastaOrigem)) {
    Write-Host "Pasta não encontrada: $pastaOrigem" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit
}

# Obter todos os arquivos da pasta
$arquivos = Get-ChildItem -Path $pastaOrigem -File

Write-Host "Iniciando renomeação dos arquivos..." -ForegroundColor Green
Write-Host "Pasta: $pastaOrigem" -ForegroundColor Cyan

foreach ($arquivo in $arquivos) {
    $nomeAtual = $arquivo.BaseName
    $extensao = $arquivo.Extension
    
    # Verificar se o nome do arquivo começa com um número seguido de ponto
    if ($nomeAtual -match "^(\d+)\.(.+)$") {
        $numeroAtual = [int]$matches[1]
        $restoDoNome = $matches[2]
        
        # Adicionar 1 ao número
        $novoNumero = $numeroAtual + 1
        
        # Criar o novo nome
        $novoNome = "$novoNumero. $restoDoNome$extensao"
        $caminhoCompleto = Join-Path $pastaOrigem $novoNome
        
        # Verificar se já existe um arquivo com o novo nome
        if (Test-Path $caminhoCompleto) {
            Write-Host "AVISO: Arquivo já existe, pulando: $novoNome" -ForegroundColor Yellow
            continue
        }
        
        try {
            # Renomear o arquivo
            Rename-Item -Path $arquivo.FullName -NewName $novoNome
            Write-Host "Renomeado: '$($arquivo.Name)' para '$novoNome'" -ForegroundColor Green
        }
        catch {
            Write-Host "ERRO ao renomear '$($arquivo.Name)': $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Pulando (não segue padrão): $($arquivo.Name)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Renomeação concluída!" -ForegroundColor Green
Read-Host "Pressione Enter para sair"