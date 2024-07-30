function Convert-YouTubeTranscript {
    <#
    .SYNOPSIS
    Converts a YouTube transcript into a structured format with timestamps and corresponding text.

    .DESCRIPTION
    This function takes a YouTube transcript as input and extracts the timestamps and their corresponding text. 
    It returns an array of custom objects, each containing a timestamp and the associated text.

    .PARAMETER transcript
    The YouTube transcript as a single string. The transcript should have timestamps in the format (MM:SS). The transcript is generated from the extension https://glasp.co/.

    .EXAMPLE
    $transcript = @"
    (00:00) on September 1st last year a team of 16 scientists made a stunning discovery that sent shock waves through the scientific Community they ...
    (05:52) essentially cease to exist for them they are momentary in a sense passing through the fabric of SpaceTime without experiencing the passage ...
    (10:09) unfolding this concept becomes even more exciting when applied to photons or particles of light photons have no clear past present or future ...
    (12:24) basic assumptions of The Big Bang Theory
    "@

    $results = Convert-YouTubeTranscript -transcript $transcript
    $results | Format-Table -AutoSize

    .OUTPUTS
    PSCustomObject
    Each object contains the following properties:
        - Timestamp: The timestamp in the format (MM:SS)
        - Text: The text corresponding to the timestamp

    .NOTES
    Author: https://github.com/voytas75
    Helper: gpt4o
    Date: 2024-07-30
    #>
    param (
        [string]$transcript
    )

    # Define the regex pattern to match timestamps in the format (MM:SS)
    $pattern = "\(\d{2}:\d{2}\)"
    
    # Find all matches of the pattern in the transcript
    $transcriptMatches = [regex]::Matches($transcript, $pattern)

    # Initialize an empty array to store the results
    $results = @()
    
    # Iterate over each match found in the transcript
    foreach ($match in $transcriptMatches) {
        # Extract the timestamp value from the match
        $timestamp = $match.Value
        
        # Determine the start index of the text following the timestamp
        $startIndex = $transcript.IndexOf($timestamp) + $timestamp.Length
        
        # Determine the end index of the text, which is the start of the next timestamp or the end of the transcript
        $endIndex = $transcript.IndexOf("(", $startIndex)
        if ($endIndex -eq -1) {
            $endIndex = $transcript.Length
        }
        
        # Extract the text between the current timestamp and the next timestamp (or end of transcript)
        $text = $transcript.Substring($startIndex, $endIndex - $startIndex).Trim()
        
        # Create a custom object with the timestamp and text, and add it to the results array
        $results += [PSCustomObject]@{
            Timestamp = $timestamp
            Text      = $text
        }
    }

    # Output the results array containing the custom objects
    return $results
}
