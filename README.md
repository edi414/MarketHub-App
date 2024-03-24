# MarketHub
 A central system for various supermarket operations, this system was created to ensure the unified management of all systems that support the company's management.

## About this Project

https://github.com/edi414/MarketHub/assets/80610321/6f068f52-d154-401d-a8af-c793c75632ab

The idea of the system is:

_"This system addresses the challenge of consolidating multiple decentralized and disconnected systems, thereby reducing operational inefficiencies and the need for manual, unsupervised tasks"._

**PS:** The current version of MarketHub is only available for local networks (localhost), only the databases are operating on a cloud-based system.

<!-- **On the Media 🤩:** A [review]() about this app (pt-BR 🇧🇷). (remove this part) -->

## Why?

Efficient management is a major challenge for supermarkets, involving reducing time wasted on operational tasks like finance, pricing, reconciliation, and catalog management. Significant time is lost in manual tasks and subscription fees for inefficient systems. Hence, this project signifies an advancement for the company, cutting costs on non-personalized system subscriptions, while boosting efficiency in commercial and administrative operations.

An example of the project's accomplishments: On average, the pricing department spends between 50 and 70 minutes pricing a purchase order with 100 SKUs. After the implementation of MarketHub, this time has reduced to an average of 13 minutes, accompanied by supervised and technology-driven execution.

Email-me: edivaldo414@gmail.com

Connect with me at [LinkedIn](https://www.linkedin.com/in/edivaldo-bezerra/).

This project is not open source, a significant portion of the code is restricted to the client.

## Some Observations about this system

1 - This project was developed for a specific client, and therefore, the complete content is restricted. Anyway, feel free to reach out with any questions or suggestions.

2 - All databases of this system are hosted in the cloud and have separate processes for data feeding. As soon as possible, I will create a repository here to share these processes.

3 - For security reasons, the step of connection with the online database will be hidden from the project, to protect the integrity of the bd.

4 - All HTML templates were built using Bootstrap as a foundation. The project's focus is to construct a consolidated backend for consuming the information inputted by users.

<!-- ## Installers

If you want to test the App in the Production mode, the installers are listed below:

[Android .apk installer](https://drive.google.com/file/d/1LKgdu1WDPo8eU2NVjoB92TPi4my8QP4D/view?usp=sharing)

iOS .ipa installer: Soon! -->

## Functionalities

- Login/logout with a user base predefined by the client (this base is static, for changes, direct input into the database is required).

- User session management: Flask session manages the content created by each user in the application.

![Markethub_login](https://github.com/edi414/MarketHub/assets/80610321/304b44ac-2202-4903-971e-6733781de409)

- Home page
    - Noticeboard: Used to highlight key points of attention for the pricing team each month.
    - Useful Links: Quick access list for essential links used in supermarket management.

![markethub](https://github.com/edi414/MarketHub/assets/80610321/5aa49753-a82c-43ba-96dc-8d739647f626)

- Pricing
    - Connection to a database containing all products and invoices received by the client, all authorized by SEFAZ.
        - To populate this database, a process was created to read the XML of client invoices and extract product and invoice information.
            - Within this process, the script suggests a minimum price for the product based on its pricing history.
    - The application queries this database to generate a table with only the information needed to validate pricing for each product.
    - The client's pricing team validates pricing and proposes changes, which, once confirmed, are inserted into a database.
    - With the data generated by the pricing team, it's possible to ensure that product prices follow the minimum margin and reduce the risk of price discrepancies on the shelf.

![markethub_precification](https://github.com/edi414/MarketHub/assets/80610321/d050a33d-ab66-4ab9-9e0e-443d7398b03f)

- Invoice Mirror Report
    - After the pricing process is completed, the application generates an invoice mirror report that has no fiscal value. This report is used by the replenishment team to ensure product price labeling on the shelves.
    - To generate this report, the application queries the database where prices have been inserted.

![markethub_espelho_nota](https://github.com/edi414/MarketHub/assets/80610321/d115f4b2-2485-4ed8-b736-4bb0a3676494)

- Contracts and Payment Plans (in development)
    - On this page, it's possible to create contracts and payment plans within minutes.
    - For the user, only filling out a form with customer registration information is necessary.
        - After this filling, the contract and payment plans are generated.
    - At the end of the process, a copy of the contract and payment plan is sent to the supermarket's and the customer's email.
    - The entire process occurs with database communication for accounts receivable management.
    - For now, this application only exists in tkinter. The next step is to transition it to the MarketHun environment (flask).

![imoveis_tkinter](https://github.com/edi414/MarketHub/assets/80610321/9790c284-30cd-497c-b879-69799d16ed0f)

- Labels (in development)
    - This page manages shelf label templates, where users can generate thermal labels for printing.
        - In this process, the application queries the Supermarket ERP API to collect the most up-to-date product information.
            - This API is local, meaning it's not available for web use, limiting remote label printing.
    - For printing, a process has been created to execute label printing through the BarTender Software via RPA.
    - Printing templates were previously provided by the client.

- Purchasing Planning (in development)
    - This page provides a suggestion of products to purchase for the week.
        - This suggestion is built through a stock counting model.

## Brainstorming

- Here share some ideas for the project:
    - Machine learning model for price suggestion with supervised learning, based on inputs from the pricing team, processed data from each invoice, and product price history in the ERP.
    - Purchase suggestions by supermarket customers, connected with the marketing team.

## Contributing

You can send how many PR's do you want, I'll be glad to analyse and accept them! And if you have any question about the project...

Email-me: edivaldo414@gmail.com

Connect with me at [LinkedIn](https://www.linkedin.com/in/edivaldo-bezerra/)

Thank you!

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/edi414/MarketHub/blob/main/LICENSE) file for details
