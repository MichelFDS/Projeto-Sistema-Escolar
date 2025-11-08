<#
PowerShell helper to initialize a local git repo, commit all files and (optionally)
create a GitHub repository using the GitHub CLI (gh) and push.

Usage:
  .\push_to_github.ps1 -RepoName "nome-do-repo" [-Private]

If GitHub CLI (gh) is installed and you're authenticated, the script will run:
  gh repo create <nome> --public --source=. --remote=origin --push

If gh is not available, the script will initialize git and print manual commands
to create a remote and push.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,

    [switch]$Private
)

function Ensure-GitInitialized {
    if (-not (Test-Path .git)) {
        Write-Host "Inicializando repositório git local..."
        git init
    } else {
        Write-Host "Repositório git já inicializado."
    }
}

function Commit-All {
    git add --all
    if (-not (git rev-parse --verify HEAD 2>$null)) {
        git commit -m "Initial commit"
    } else {
        git commit -m "Update" || Write-Host "Nada para commitar."
    }
}

Ensure-GitInitialized
Commit-All

# If gh is installed, create the repo remotely and push
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host "GitHub CLI detectado. Criando o repositório remoto e enviando..."
    $flags = "--public"
    if ($Private) { $flags = "--private" }
    # gh repo create <name> --source=. --remote=origin --push [--public|--private]
    gh repo create $RepoName --source=. --remote=origin --push $flags
    if ($LASTEXITCODE -eq 0) { Write-Host "Repositório criado e push realizado com sucesso." }
    else { Write-Host "gh retornou erro. Verifique a saída acima." }
} else {
    Write-Host "\nGitHub CLI ('gh') não encontrado. Para criar remote automaticamente instale 'gh' e faça 'gh auth login'."
    Write-Host "Comandos manuais a executar (substitua <USERNAME> e <REPO>):\n"
    Write-Host "1) Crie o repositório no GitHub pelo site: https://github.com/new (nome: $RepoName)"
    Write-Host "2) Adicione o remote e envie:\n"
    Write-Host "   git remote add origin https://github.com/<USERNAME>/$RepoName.git"
    Write-Host "   git branch -M main"
    Write-Host "   git push -u origin main"
}

Write-Host "\nConcluído. Se criou o repositório remotamente, cole aqui a URL pública para eu validar/ajudar a testar."
