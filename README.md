# Welcome to VoytasCodeLab

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/A0A6KYBUS)

Explore a diverse collection of my scripts, snippets, and functions across multiple programming languages. Whether you're working with PowerShell, Python, Bash, JavaScript, or more, **VoytasCodeLab** provides a valuable resource for automation, development, and learning. Dive into various coding examples and enhance your programming toolkit with Voytas.

## The Code

1. ### [Google Knowledge Graph Search Tool](./thecode/crewAI/config/google_KGS_tool.py)

    [Python] [[CrewAI](https://github.com/crewAIInc/crewAI)] [[Google Knowledge Graph API](https://developers.google.com/knowledge-graph/)]

    The `google_KGS_tool.py` script is designed to perform searches using the Google Knowledge Graph Search API. 

    **Key Features:**
    - **Search Query**: Specify a literal string to search for in the Knowledge Graph.
    - **Result Limit**: Limits the number of entities to be returned. Maximum is 500. Default is 10.
    - **Language Support**: Specify the list of language codes to run the query with.
    - **Type Restriction**: Restricts returned entities to those of the specified types.
    - **Prefix Match**: Enables prefix (initial substring) match against names and aliases of entities.

2. ### [CrewAI Tech Discussion Assistant](./thecode/crewAI/crewai-PROD-TechDiscussionAssistant.py)

    [Python] [[CrewAI](https://github.com/crewAIInc/crewAI)] [Azure OpenAI]

    The `crewai-PROD-TechDiscussionAssistant.py` script is designed to run CrewAI for technical discussions and assistance. This script allows users to specify a topic for discussion and provides various modes such as planning and manager modes. It utilizes configurations and tools from the CrewAI framework to facilitate discussions and generate professional reports.

    **Key Features:**
    - **Topic Discussion**: Specify a topic for in-depth technical discussion.
    - **Multiple Modes**: Enable planning and manager modes for hierarchical or sequential processing.
    - **Verbose Output**: Option to enable detailed output for better insights.
    - **Result Count**: Specify the number of web results to retrieve.
    - **Caching and Memory Options**: Enable or disable caching and memory for the crew.
    - **Agent-Based Tasks**: Utilizes specialized agents for tasks such as web search, data verification, relevance analysis, and report writing.
    - **Markdown Reports**: Generates structured markdown-formatted reports with detailed sections including responses, findings, recommendations, and timelines.

    **Example Usage:**

    ```python
    python crewai-PROD-TechDiscussionAssistant.py --topic "What's new in Windows Server" --result_count 5
    ```

    **Source Code**: [crewai-PROD-TechDiscussionAssistant.py](./thecode/crewAI/crewai-PROD-TechDiscussionAssistant.py)

3. ### [CrewAI News Analyzer](./thecode/crewAI/crewai-PROD-News_analyzer_A2_v2.py)

    [Python] [[CrewAI](https://github.com/crewAIInc/crewAI)] [Azure OpenaAI]

    The `crewai-PROD-News_analyzer_A2_v2.py` script is designed to run CrewAI for comprehensive news search and analysis. This script allows users to specify a topic for analysis and provides various modes such as planning and manager modes. It utilizes configurations and tools from the CrewAI framework to perform detailed analysis and generate professional reports.

    **Key Features:**
    - **Topic Analysis**: Specify a topic for in-depth news analysis.
    - **Multiple Modes**: Enable planning and manager modes for hierarchical or sequential processing.
    - **Verbose Output**: Option to enable detailed output for better insights.
    - **Result Count**: Specify the number of web results per provider to retrieve.
    - **Caching and Memory Options**: Enable or disable caching and memory for the crew.
    - **Agent-Based Tasks**: Utilizes specialized agents for tasks such as web search, data verification, trend analysis, and report writing.
    - **Markdown Reports**: Generates structured markdown-formatted reports with detailed sections including trends, findings, recommendations, and timelines.

    **Example Usage:**

    ```python
    python crewai-PROD-News_analyzer_A2_v2.py --topic "What's new in Windows Server" --planning --verbose --result_count 5
    ```

    **Source Code**: [crewai-PROD-News_analyzer_A2_v2.py](./thecode/crewAI/crewai-PROD-News_analyzer_A2_v2.py)

4. ### [Get-CyclomaticComplexity](https://www.powershellgallery.com/packages/Get-CyclomaticComplexity)

    [PowerShell]

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

5. ### [Random numbers](https://gist.github.com/voytas75/9010339feae5f2c16aab3b4e4db6c801)

   [PowerShell]

    A script to generate a series of random numbers using different methods and formats.

    The script uses both built-in PowerShell capabilities and .NET classes to generate random numbers. It showcases different ways to generate random numbers as UInt64 and UInt32, both as a full range and a fractional number between 0 and 1.

    **If you need random numbers for cryptographic purposes, it's recommended to use classes from "System.Security.Cryptography", such as "RandomNumberGenerator", which provides cryptographic strength random number generation.**
    >

    [Linkedin](https://www.linkedin.com/feed/update/urn:li:activity:7149346690402074624?utm_source=share&utm_medium=member_desktop)

    [random.ps1](https://gist.github.com/voytas75/9010339feae5f2c16aab3b4e4db6c801)

6. ### [Convert-YouTubeTranscript](./thecode/Convert-YouTubeTranscript.ps1)

   [PowerShell]

    Converts a YouTube transcript into a structured format with timestamps and corresponding text.

    This script takes a YouTube transcript ([glasp.co - transcript extension](https://glasp.co/)) as input and extracts the timestamps and their corresponding text. It returns an array of custom objects, each containing a timestamp and the associated text.

    **Example**

    ```powershell
    $transcript = @"
    (00:00) on September 1st last year a team of 16 scientists made a stunning discovery that sent shock waves through the scientific Community they ...
    (05:52) essentially cease to exist for them they are momentary in a sense passing through the fabric of SpaceTime without experiencing the passage ...
    (10:09) unfolding this concept becomes even more exciting when applied to photons or particles of light photons have no clear past present or future ...
    (12:24) basic assumptions of The Big Bang Theory
    "@

    $results = Convert-YouTubeTranscript -transcript $transcript
    $results | Format-Table -AutoSize
    ```

    [Source code](./thecode/Convert-YouTubeTranscript.ps1)

    [transcript extension](https://glasp.co/)

7. ### [Get-ADUserACLsAndExtendedRights](./thecode/Get-ADUserACLsAndExtendedRights.ps1)

   [PowerShell]

    Retrieves the Access Control List (ACL) and Extended Rights for a specified Active Directory user.

    This script fetches the ACL for a user object in Active Directory and maps any Extended Rights GUIDs to their corresponding names. It outputs the ACL entries in a formatted table.

    **Example**

    ```text
    IdentityReference                            ActiveDirectoryRight       ExtendedRightName     ExtendedRightGUID
    -----------------                            --------------------       -----------------     -----------------
    XYZ\TASK-T2-User-ResetPassword                      ExtendedRight          Reset Password     00299570-246d-11d0-a768-00aa006e0529
    XYZ\TASK-T2-User-Move                               ExtendedRight          Reset Password     00299570-246d-11d0-a768-00aa006e0529
    XYZ\TASK-T2-User-DisableEnable                      WriteProperty          N/A                N/A                                 
    XYZ\TASK-T2-User-MemberOf                           WriteProperty          N/A                N/A                                 
    XYZ\TASK-T2-User-ResetPassword        ReadProperty, WriteProperty          N/A                N/A                                 
    XYZ\TASK-T2-User-Move                    CreateChild, DeleteChild          N/A                N/A                                 
    XYZ\TASK-T2-User-Move                               WriteProperty          N/A                N/A                                 
    ```

    [Source code](./thecode/Get-ADUserACLsAndExtendedRights.ps1)
