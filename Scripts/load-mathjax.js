//===============================================================================
//
// load-mathjax.js
//
// Script for configuring and loading MathJax in my web pages.  See instructions
// for "Configuring and Loading in One Script",
//
//     https://docs.mathjax.org/en/latest/web/configuration.html
//
// and for hosting your own copy of MathJax on your server, 
//
//     https://docs.mathjax.org/en/latest/web/hosting.html
//
// Put this command in the <head> section of your html before loading the style sheet:
//
//     <script src="../Scripts/load-mathjax.js" async></script>
//
//===============================================================================

// The variable "window" is the current web page URL, including the #section location.

// Configure MathJax before you load it.  
// The documented settings are described in
//     https://docs.mathjax.org/en/stable/options/HTML-CSS.html
window.MathJax =
{
  // Set both the default math delimiters \(...\) and the ones I prefer:  $ and $$.
  tex: 
  {
    inlineMath: [['$', '$'], ['\\(', '\\)']]
  },

  svg: 
  {
    fontCache: 'global'
  },
} ;

// Next, load MathJax.
// See the configuration documeent,
//     https://docs.mathjax.org/en/latest/web/configuration.html
// -On my development machines and on my web server, load a local copy of MathJax.
// -Otherwise load from the MathJax CDN server.
(function()  // Define a function and call it immediately.
{
    // This function will create the HTML code,
    // <script>
    //      MathJax setup commands 
    // </script>
    var script = document.createElement( 'script' ) ;

    // The file:/// protocol says the web site is hosted on the current machine's file system.
    if (window.location.protocol.match( /file:/ ))
    {
        // Hosted on my macOS development computer.
        if (window.location.pathname.match( /Users\/seanoconnor/ ))
        {
            // Use a local copy of MathJax.  I downloaded MathJax as follows:
            //     cd WebSite
            //     git clone https://github.com/mathjax/MathJax.git mathjax
            //     cd mathjax
            //     git fetch --all --tag --prune
            //     git remote -vv
            //         origin	https://github.com/mathjax/MathJax.git (fetch)
            //         origin	https://github.com/mathjax/MathJax.git (push)
            //
            // You should be in the master branch by default,
            //     git branch
            //         * master
            //
            // Pull to get the latest updates
            //     git pull
            //
            // You can see which tags are available using
            //     git tag
            //        ...
            //        3.1.4
            //        4.0.0
            //
            // For local testing of MathJax versions, you can fetch a particular version,
            //     git checkout tags/4.0.0 -b v4.0.0
            //     git branch
            //         master
            //         v3.1.4
            //       * v4.0.0
            //
            // NOTE:
            // If you want to host MathJax files on your own server, load this script,
            //
            script.src="/Users/seanoconnor/Desktop/Sean/WebSite/mathjax/tex-chtml.js";

            // To see this message in Firefox, open Tools->Browser Tools -> Web Developer Tools then select the Console tab.
            console.log( "Mac OS:  Prepare to load MathJax from local directory location " + script.src ) ;
        }
        // Hosted on my Ubuntu Linux development computer.
        else if (window.location.pathname.match( /home\/seanoconnor/ ))
        {
            script.src="/home/seanoconnor/Desktop/Sean/WebSite/mathjax/tex-chtml.js";

            // In Firefox, open Tools->Web Developer->Web Console to see this message:
            console.log( "Ubuntu Linux:  Prepare to load MathJax from local directory location " + script.src ) ;
        }
        // Can't figure it out?  Load from CDN MathJax server.
        else
        {
            // This recommended URL will load the latest version from the default CDN MathJax server.
            script.src = 'https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg.js' ;
            script.defer = true ;
            console.log( "Unknown Computer:  Prepare to load MathJax from CDN server location " + script.src ) ;
        }
    }
    // Hosted on my web server.
    else if (window.location.hostname.match( /seanerikoconnor.freeservers.com/ ))
    {
        // Load from a local copy of MathJax on my web server.
        script.src="/mathjax/tex-chtml.js";
        console.log( "Freeservers Web Host:  Prepare to load MathJax from local directory location " + script.src ) ;
    }
    // Hosted on some other web server.
    else
    {
        // This recommended URL will load the latest version from the default CDN MathJax server.
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg.js' ;
        script.defer = true ;
        console.log( "Unknown Web Host:  Prepare to load MathJax from CDN server location " + script.src ) ;
    }

    script.async = true ;
  
    // Place the generated MathJax configuration and loading script into the html 
    // file in the <head>...</head> section.
    document.head.appendChild( script ) ;
    console.log( "Loading MathJax into HTML document inside newly created <script> ... </script>" ) ;

})();
