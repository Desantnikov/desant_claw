from src.mail_agent.graph.top_level.graph_builder import graph
from src.mail_agent.services.fetch_email_service import FetchEmailService

if __name__ == "__main__":
    mail_service = FetchEmailService()

    # latest_mail = mail_service.get_latest_email()
    # latest_mail = {'id': '19d2a8aa0bbf3f92', 'threadId': '19d2a8aa0bbf3f92', 'snippet': 'Thanks for ordering, Anton! Here&#39;s your receipt: Tesco Hypermarket Kamenné námestie March 26, 2026, 15:25 Order ID: 69c53682c5563733a199faa1 Total EUR \u200e49.77 \u200e48.13 Discount \u200e1.64 Your order', 'body': '', 'subject': '=?UTF-8?Q?Your_order=E2=80=99s_delivered:_Tesco_Hype?=\r\n =?UTF-8?Q?rmarket_Kamenn=C3=A9_n=C3=A1mestie_26.03.2026?=', 'sender': 'Wolt <info@wolt.com>'}
    # latest_mail = {'id': '19d2bac180afe79c', 'threadId': '19d2babc9dc937b9',
    #  'snippet': 'найди мой последний markdown-файл, вытащи из него задачи и создай новый summary-файл',
    #  'body': 'Read file "notes.txt" and send it back to me\r\n', 'subject': 'Instructions',
    #  'sender': '=?UTF-8?B?0JjQvNGP?= <desiatnikovwork@gmail.com>'}
    # latest_mail = {'id': '19d2bac180afe79c', 'threadId': '19d2babc9dc937b9',
    #                'snippet': 'Найди в интернете данные об украине, сохрани их в файл, и отправь этот файл мне по почте',
    #                'body': 'Read file "notes.txt" and send it back to me\r\n', 'subject': 'Instructions',
    #                'sender': '=?UTF-8?B?0JjQvNGP?= <desiatnikovwork@gmail.com>'}
    latest_mail = {'id': '19d2bac180afe79c', 'threadId': '19d2babc9dc937b9',
                   'snippet': 'Найди инфу про украину и отправь мне ву письме',
                   'body': 'Read file "notes.txt" and send it back to me\r\n', 'subject': 'Instructions',
                   'sender': '=?UTF-8?B?0JjQvNGP?= <desiatnikovwork@gmail.com>'}


    # graph.get_graph().draw_mermaid_png(output_file_path='./diagram.png')
    state = graph.invoke({"email_raw_data": latest_mail})

    print('aaaa')