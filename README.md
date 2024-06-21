# Welcome to VoytasCodeLab

Explore a diverse collection of my scripts, snippets, and functions across multiple programming languages. Whether you're working with PowerShell, Python, Bash, JavaScript, or more, **VoytasCodeLab** provides a valuable resource for automation, development, and learning. Dive into various coding examples and enhance your programming toolkit with Voytas.

## The Code

1. ### Get-CyclomaticComplexity

    Calculates the cyclomatic complexity of a PowerShell script or code block, including both functions and top-level code.

    [![PowerShell Gallery](https://img.shields.io/powershellgallery/dt/Get-CyclomaticComplexity)](https://www.powershellgallery.com/packages/Get-CyclomaticComplexity)

    Published version: [Powershell gallery](https://www.powershellgallery.com/packages/Get-CyclomaticComplexity)

    [Source code](./thecode/Get-CyclomaticComplexity.ps1)

    **Example**

    ```powershell
    $code = @"
        if ($true) { Write-Output "True" }
        else { Write-Output "False" }
        function Test {
            if ($true) { Write-Output "True" }
            else { Write-Output "False" }
        }
        "@
    Get-CyclomaticComplexity -CodeBlock $code
    ```

    ```powershell
    Get-CyclomaticComplexity -CodeBlock (Get-Content "D:\path\to\file.ps1" -raw)
    ```

    ```powershell
    Get-CyclomaticComplexity -FilePath "C:\path\to\file.ps1"
    ```
