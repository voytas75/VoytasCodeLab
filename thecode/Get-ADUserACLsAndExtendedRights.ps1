<#
.SYNOPSIS
    Retrieves and displays the Access Control List (ACL) and Extended Rights for a specified Active Directory user.

.DESCRIPTION
    This script retrieves the ACL for a specified Active Directory user and displays all ACL entries, including any extended rights.
    It maps the ObjectType GUID to its corresponding Extended Right name if applicable.

.PARAMETER sAMAccountName
    The sAMAccountName of the user for whom the ACL and extended rights are to be retrieved.

.EXAMPLE
    .\Get-ADUserACLsAndExtendedRights.ps1 -sAMAccountName "jdoe"
    Retrieves and displays the ACL and extended rights for the user with sAMAccountName "jdoe".

.NOTES
    Author: https://github.com/voytas75
    Helper: gpt4o
    Date: 2024-10-28
#>

# Define the sAMAccountName of the user
$sAMAccountName = "username"  # Replace 'username' with the actual sAMAccountName

# Import Active Directory module if not already loaded
if (!(Get-Module -ListAvailable -Name ActiveDirectory)) {
    Import-Module ActiveDirectory
}

# Get the Distinguished Name (DN) of the user object
$UserDN = (Get-ADUser -Identity $sAMAccountName -Properties DistinguishedName).DistinguishedName

# Retrieve the ACL for the user object
$ACL = Get-ACL -Path "AD:$UserDN"

# Define a function to map the ObjectType GUID to its Extended Right name
function Get-ExtendedRightName {
    param ([string]$Guid)

    # Define the search base for Extended Rights in the Configuration partition
    $ExtendedRightsPath = "CN=Extended-Rights," + (Get-ADRootDSE).ConfigurationNamingContext

    # Search for the Extended Right in the Configuration naming context by rightsGuid
    $Right = Get-ADObject -Filter "rightsGuid -eq '$Guid'" -SearchBase $ExtendedRightsPath -Properties displayName -ErrorAction SilentlyContinue

    if ($Right) {
        return $Right.displayName
    } else {
        return "Unknown Extended Right ($Guid)"
    }
}

# Display all ACL entries
Write-Host "Displaying all ACL entries for user: $sAMAccountName"
$ACL.Access | ForEach-Object {
    $ExtendedRightName = if ($_.ActiveDirectoryRights -eq 'ExtendedRight') {
        Get-ExtendedRightName -Guid $_.ObjectType
    } else {
        "N/A"
    }

    [PSCustomObject]@{
        IdentityReference      = $_.IdentityReference
        ActiveDirectoryRight   = $_.ActiveDirectoryRights
        ExtendedRightName      = $ExtendedRightName
        ExtendedRightGUID      = if ($_.ActiveDirectoryRights -eq 'ExtendedRight') { $_.ObjectType } else { "N/A" }
        InheritanceType        = $_.InheritanceType
        ObjectType             = $_.ObjectType
        InheritedObjectType    = $_.InheritedObjectType
        IsInherited            = $_.IsInherited
        AccessControlType      = $_.AccessControlType
    }
} | Format-Table -AutoSize
