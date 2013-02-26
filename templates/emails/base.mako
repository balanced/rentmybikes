<%
from datetime import datetime
%>
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8">
    ${ self.cssdefs() }
</head>
<body>
    <div id="header">
        Rent my bike!
    </div>
    <div id="main">
        ${ next.body() }
    </div>
    <p class="footer">Balanced &copy; 2012 - Generated ${ datetime.utcnow() }</p>
</body>
</html>

<%def name="cssdefs()">
<style type="text/css">
    body {
        font-size: 13px;
        font-family: "Helvetica Neue", "Times New Roman", Arial, sans-serif;
        width: 700px;
        margin: 0 auto;
        background-color: #e6e6e6;
        background-image: url(http://www.rentmybike.co/images/background.png);
    }
    #header {

    }
    #main {
        padding: 20px;
        background-color: white;
        border: 1px solid #ccc;
    }
    .footer { text-align:center; font-size: 11px; }
</style>
</%def>
