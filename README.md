<h2> SENSS </h2>

SENSS - software-defined security service is a framework that enables a victim network to request services from remote ISPs for traffic that carries source IPs or destination IPs from this net work's address space. These services range from statistics gathering, to filtering or quality of service guarantees, to route reports or modifications. The SENSS service has very simple, yet powerful, interfaces. This enables it to handle a variety of data plane and control plane attacks, while being easily implementable in today's ISP. Through extensive evaluations on realistic traffic traces and Internet topology, we show how SENSS can be used to quickly, safely and effectively mitigate a variety of large-scale attacks that are largely unhandled today. 

![Output sample](https://github.com/STEELISI/SENSS/raw/master/doc/senss.gif)

<h2> Setup </h2>

```git pull https://github.com/STEELISI/SENSS.git```

```cd SENSS/Setup```

Requirements for running SENSS Client
- mysqldb
- apache2
- php5, ensure that the file_upload flag is set to 1 in php.ini file. 

```sudo python setup.py```

The setup will prompt for:
- type of installation which can be either for client, server or proxy
- mysqldb password
- root password (required to install dependencies and access the apache2 files)

