<#PSScriptInfo
.VERSION 1.0.1
.GUID 74b3a6a0-ec1b-459e-869a-5cafe8f744e3
.AUTHOR https://github.com/voytas75
.TAGS Cyclomatic, Complexity, Script, Function
.PROJECTURI 
.RELEASENOTES
1.0.1: initializing.
#>

function Get-CyclomaticComplexity {
    <#
    .SYNOPSIS
        Calculates the cyclomatic complexity of functions in a given PowerShell script or code block.
    .DESCRIPTION
        This function analyzes the provided PowerShell script file or code block to calculate the cyclomatic complexity of each function defined within it.
        The cyclomatic complexity score is interpreted as follows:
        1: The function has a single execution path with no control flow statements (e.g., if, else, while, etc.). This typically means the function is simple and straightforward.
        2 or 3: Functions with moderate complexity, having a few conditional paths or loops.
        4-7: These functions are more complex, with multiple decision points and/or nested control structures.
        Above 7: Indicates higher complexity, which can make the function harder to test and maintain.
    .PARAMETER FilePath
        The path to the PowerShell script file to be analyzed.
    .PARAMETER CodeBlock
        A string containing the PowerShell code block to be analyzed.
    .EXAMPLE
        Get-CyclomaticComplexity -FilePath "C:\Scripts\MyScript.ps1"
    .EXAMPLE
        $code = @"
        function Test {
            if ($true) { Write-Output "True" }
            else { Write-Output "False" }
        }
        "@
        Get-CyclomaticComplexity -CodeBlock $code
    .NOTES
        Author: https://github.com/voytas75
        Date: 2024-06-17
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
    
    if ($functions.Count -eq 0) {
        Write-Information "-- No functions found for cyclomatic complexity analysis." -InformationAction Continue
        return $false
    }

    foreach ($function in $functions) {
        $cyclomaticComplexity = 1
        # Filter tokens that belong to the current function
        $functionTokens = $tokens | Where-Object { $_.Extent.StartOffset -ge $function.Extent.StartOffset -and $_.Extent.EndOffset -le $function.Extent.EndOffset }
        $observedBlocks = @()

        foreach ($token in $functionTokens) {
            if ($token.Kind -in 'If', 'ElseIf', 'Catch') {
                $cyclomaticComplexity++
            }
            elseif ($token.Kind -in 'While', 'For', 'Switch') {
                $cyclomaticComplexity++
                $observedBlocks += $token
            }
            elseif ($token.Kind -in 'EndWhile', 'EndFor', 'EndSwitch') {
                $observedBlocks = $observedBlocks | Where-Object { $_ -ne $token }
            }
        }

        # Determine the complexity description
        $description = switch ($cyclomaticComplexity) {
            1 { "The function has a single execution path with no control flow statements. This typically means the function is simple and straightforward." }
            { $_ -in 2..3 } { "Functions with moderate complexity, having a few conditional paths or loops." }
            { $_ -in 4..7 } { "These functions are more complex, with multiple decision points and/or nested control structures." }
            default { "Indicates higher complexity, which can make the function harder to test and maintain." }
        }

        Write-Output "$($function.Name) : $cyclomaticComplexity - $description"
    }
}