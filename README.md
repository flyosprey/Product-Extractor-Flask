<h1>In progress...</h1>

<h1>How it works</h1>

<h3>There two separated projects Flask and Scrapy.</h3>
<h3>The Flask side tigger the Scrapy side to extract data.</h3>
<h3>All extracted data collects in PostgresQL database</h3>

<h1>How to Use it</h1>
<ol>
    <li>Install the repository to local machine</li>
    <li>Create venv and install all requirements</li>
    <li>Create PostgresQL database</li>
    <li>Then create <b>credentials.py</b> in the <b>flask_app</b> directory</li>
    <li>Create requirement variables for PostgresQL and Flask</li>
</ol>

<h4>Requirement variables for:</h4>
<h4>PostgresQL:</h4>
<ol style="font-weight: bold;">
    <li>HOSTNAME</li>
    <li>USERNAME</li>
    <li>PASSWORD</li>
    <li>DATABASE</li>
</ol>
<h4>Flask:</h4>
<ol style="font-weight: bold;">
    <li>SECRET_KEY</li>
</ol>

<h3>Finally run app.py as Flask</h3>
