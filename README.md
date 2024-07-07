# Welcome to VoytasCodeLab

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/A0A6KYBUS)

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

2. ### Random numbers

    A script to generate a series of random numbers using different methods and formats.

    The script uses both built-in PowerShell capabilities and .NET classes to generate random numbers. It showcases different ways to generate random numbers as UInt64 and UInt32, both as a full range and a fractional number between 0 and 1.

    **If you need random numbers for cryptographic purposes, it's recommended to use classes from "System.Security.Cryptography", such as "RandomNumberGenerator", which provides cryptographic strength random number generation.**
    >

    [Linkedin](https://www.linkedin.com/feed/update/urn:li:activity:7149346690402074624?utm_source=share&utm_medium=member_desktop)

    [random.ps1](https://gist.github.com/voytas75/9010339feae5f2c16aab3b4e4db6c801)

