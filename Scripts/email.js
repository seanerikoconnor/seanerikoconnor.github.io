// JavaScript for hiding my email address from spambots yet it works as usual.
//
// (1) Load this JavaScript code in the html header section (before </head>):
//
//     <script>
//     <!--
//         document.write( mailto( "Some Mail Message" ) ) ;  // Generate HTML mail header on-the-fly without revealing the email address.
//     // -->
//     </script>
//
//  (2) It will generate this equivalent HTML:
//
//     <a href="mailto:my_email_address">Some Mail Message</a>
//
//  Thanks to 
//
//     http://www.grall.name/posts/1/antiSpam-emailAddressObfuscation.html
//
function mailto( mailMessage )
{
    return mailtoPrefix() + mailMessage + mailSuffix() ;
}

function mailtoPrefix()
{
    var mailDirective = "mailto:" ;
    var realAddress = "" ; 

    realAddress += decode( generateScrambledMailAdddress() ) ;

    return '<a href="' + mailDirective + realAddress + '\">' ;
}

function mailSuffix()
{
    return '</a>' ;
}

function generateScrambledMailAdddress()
{
    // My email address in encoded form from the encode() function below.
    var scrambledMailAddress = "|x|zW~xEz" ;
    return scrambledMailAddress ;
}

function codeToChar( code )
{
    // Unicode character from an integer between 0 and 65535 (0xFFFF). Numbers greater than 0xFFFF are truncated.
    return String.fromCharCode( code ) ;
}

function charToCode( ch )
{
    // Returns an integer between 0 and 65535 representing the UTF-16 code unit at string index 0.
    return ch.charCodeAt( 0 ) ;
}

function encode( plainText )
{
    // Encode a string.

    var cypherText = "" ;
    var offset = 23 ;

    for (var i = 0 ;  i < plainText.length ; ++i)
        cypherText += codeToChar( charToCode( plainText[ i ] ) + offset ) ;

    return cypherText ;
}

function decode( cypherText )
{
    // Decode a string.

    var plainText = "" ;
    var offset = -23 ;

    for (var i = 0 ;  i < cypherText.length ; ++i)
        plainText += codeToChar( charToCode( cypherText[ i ] ) + offset ) ;

    return plainText ;
}

