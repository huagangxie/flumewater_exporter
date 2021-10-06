# flumewater_exporter
Flume Water exporter for Prometheus

Flume API https://flumetech.readme.io/reference


How to build 

1. use the 
    $ sudo docker build -t flumewater_exporter . 

2. get your clientid, clientsecret from the flumeportal
    https://portal.flumewater.com/settings
    Click on API Access, and generate the secret.
    
4. run the container 
    $ sudo docker run -d --restart=always -p 9183:9183 flumewater_exporter --clientid XXXXXXX --clientsecret XXXXXXXXXXXXXX --username "your flume login" --password "your_pass" --verbose 
       



Credit:
    Get a of the code template from following two projects

 * Eagle Exporter https://github.com/sbrudenell/eagle_exporter
 * FlumeCLI https://github.com/ScriptBlock/flumecli
 * API Reference https://flumetech.readme.io/reference
