<#PSScriptInfo
.VERSION 1.1.0
.DESCRIPTION Calculates the cyclomatic complexity of a PowerShell script or code block, including both functions and top-level code.
.GUID 74b3a6a0-ec1b-459e-869a-5cafe8f744e3
.AUTHOR https://github.com/voytas75
.TAGS Cyclomatic, Complexity, Script, Function
.PROJECTURI https://github.com/voytas75/VoytasCodeLab#get-cyclomaticcomplexity
.RELEASENOTES
1.1.0: Added analysis of top-level code outside of functions.
#>

function Get-CyclomaticComplexity {
    <#
    .SYNOPSIS
        Calculates the cyclomatic complexity of a PowerShell script or code block, including both functions and top-level code.
    .DESCRIPTION
        This function analyzes the provided PowerShell script file or code block to calculate the cyclomatic complexity of each function defined within it, as well as the complexity of any code outside functions.
        The cyclomatic complexity score is interpreted as follows:
        1: The code has a single execution path with no control flow statements (e.g., if, else, while, etc.). This typically means the code is simple and straightforward.
        2 or 3: Code with moderate complexity, having a few conditional paths or loops.
        4-7: More complex code, with multiple decision points and/or nested control structures.
        Above 7: Indicates higher complexity, which can make the code harder to test and maintain.
    .PARAMETER FilePath
        The path to the PowerShell script file to be analyzed.
    .PARAMETER CodeBlock
        A string containing the PowerShell code block to be analyzed.
    .EXAMPLE
        Get-CyclomaticComplexity -FilePath "C:\Scripts\MyScript.ps1"
    .EXAMPLE
        $code = @"
        if ($true) { Write-Output "True" }
        else { Write-Output "False" }
        function Test {
            if ($true) { Write-Output "True" }
            else { Write-Output "False" }
        }
        "@
        Get-CyclomaticComplexity -CodeBlock $code
    .NOTES
        Author: https://github.com/voytas75
        Date: 2024-06-21
    #>
    param(
        [Parameter(Mandatory = $false)]
        [string]$FilePath,
        [Parameter(Mandatory = $false)]
        [string]$CodeBlock
    )

    # Initialize tokens array
    $tokens = @()

    if ($FilePath) {
        if (Test-Path $FilePath -PathType Leaf) {
            # Parse the script file
            $ast = [System.Management.Automation.Language.Parser]::ParseInput((Get-Content -Path $FilePath -Raw), [ref]$tokens, [ref]$null)
        }
        else {
            Write-Error "File '$FilePath' does not exist."
            return
        }
    }
    elseif ($CodeBlock) {
        # Parse the code block
        $ast = [System.Management.Automation.Language.Parser]::ParseInput($CodeBlock, [ref]$tokens, [ref]$null)
    }
    else {
        Write-Error "No FilePath or CodeBlock provided for analysis."
        return
    }

    # Identify and loop through all function definitions
    $functions = $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)

    # Initialize total complexity for the script
    $totalComplexity = 1

    # Calculate complexity for functions
    foreach ($function in $functions) {
        $functionComplexity = 1
        # Filter tokens that belong to the current function
        $functionTokens = $tokens | Where-Object { $_.Extent.StartOffset -ge $function.Extent.StartOffset -and $_.Extent.EndOffset -le $function.Extent.EndOffset }

        foreach ($token in $functionTokens) {
            if ($token.Kind -in 'If', 'ElseIf', 'Catch', 'While', 'For', 'Switch') {
                $functionComplexity++
            }
        }

        # Output function complexity
        Write-Output "$($function.Name) : $functionComplexity - $(Get-ComplexityDescription $functionComplexity)"
    }

    # Calculate complexity for top-level code (code outside of functions)
    $globalTokens = $tokens | Where-Object { 
        $global = $true
        foreach ($function in $functions) {
            if ($_.Extent.StartOffset -ge $function.Extent.StartOffset -and $_.Extent.EndOffset -le $function.Extent.EndOffset) {
                $global = $false
                break
            }
        }
        $global
    }

    foreach ($token in $globalTokens) {
        if ($token.Kind -in 'If', 'ElseIf', 'Catch', 'While', 'For', 'Switch') {
            $totalComplexity++
        }
    }

    # Output global complexity
    Write-Output "Global : $totalComplexity - $(Get-ComplexityDescription $totalComplexity)"
}

# Helper function to get complexity description
function Get-ComplexityDescription {
    param (
        [int]$complexity
    )
    switch ($complexity) {
        1 { "The code has a single execution path with no control flow statements. This typically means the code is simple and straightforward." }
        { $_ -in 2..3 } { "Code with moderate complexity, having a few conditional paths or loops." }
        { $_ -in 4..7 } { "More complex code, with multiple decision points and/or nested control structures." }
        default { "Indicates higher complexity, which can make the code harder to test and maintain." }
    }
}