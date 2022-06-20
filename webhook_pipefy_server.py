from flask import Flask, request, abort
import requests
import json
app = Flask(__name__)

pipefy_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjp7ImlkIjozMDIwODM5NTUsImVtYWlsIjoidmluaWNpdXNzYW50b3NAY29uc3VsdG9yaWFmb2N1cy5jb20iLCJhcHBsaWNhdGlvbiI6MzAwMTY1NzYzfX0.OY0vojb_qVIaWmlk8up-zAfkOEjUOM6Np_jWelxFcf52GCstImDtkCfJVPOEH32lI7zFCH-cMISlMWJ4PhBeXQ"
#labels: Alta Prioridade/Media Prioridade/Baixa Prioridade
labels = ["307204769", "307204774", "307204781"]

url = "https://api.pipefy.com/graphql"
pipe_id = '301288261'
pipe_id_MKT_PWR = '301714308'
headers = {
    "authorization": f"Bearer {pipefy_token}",
    "content-type": "application/json"
}

@app.route('/create_card_MKT_RedeSocial', methods=['POST'])
def create_card_MKT_RedeSocial():
    print("aaa")
    if request.method == 'POST':
        print("Data received from Webhook is: ", request.json)
        json_data = request.json
        id_card = str(json_data['data']['card']['id'])
        print(f"ID card: {id_card}")
        hasNextPage = True
        first_query = True
        while (hasNextPage):
            if (first_query):
                payload = {
                    "query": "{allCards(pipeId: \"" + pipe_id + "\") { edges { node { id title assignees {id} fields {name value}}}pageInfo{endCursor hasNextPage}}}"}
                first_query = False
            else:
                payload = {
                    "query": "{allCards(pipeId: \"" + pipe_id + "\", after:\"" + end_cursor + "\") { edges { node { id title assignees {id} fields {name value}}}pageInfo{endCursor hasNextPage}}}"}
            response = requests.request("POST", url, json=payload, headers=headers)
            json_data = json.loads(response.text)
            print(json_data)
            end_cursor = json_data["data"]["allCards"]["pageInfo"]["endCursor"]
            hasNextPage = json_data["data"]["allCards"]["pageInfo"]["hasNextPage"]
            total_cards = len(json_data["data"]["allCards"]["edges"])
            for i in range(total_cards):
                card_id = json_data["data"]["allCards"]["edges"][i]["node"]["id"]
                if(card_id == id_card):
                    card_id = json_data["data"]["allCards"]["edges"][i]["node"]["id"]
                    card_assignee = json_data["data"]["allCards"]["edges"][i]["node"]["assignees"]
                    card_data_d = json_data["data"]["allCards"]["edges"][i]["node"]["fields"]
                    card_data = {x['name']: x['value'] for x in card_data_d}
                    card_title = json_data["data"]["allCards"]["edges"][i]["node"]["title"]
                    card_responsavel = card_data["Responsável"]
                    card_ser_feito = card_data["O que precisa ser feito?"]
                    card_prazo = card_data["Prazo"]
                    card_prioridade = card_data["Prioridade"]
                    print(card_assignee)
                    print(card_responsavel)
                    print(card_ser_feito)
                    print(card_prazo)
                    print("Prioridade")
                    print(type(card_prioridade))
                    print(card_prioridade[0])
                    print(card_prioridade == "Alta Prioridade")
                    if card_prioridade[0] == "Alta Prioridade":
                        label_id = labels[0]
                    elif card_prioridade[0] == "Média Prioridade":
                        label_id = labels[1]
                    else:
                        label_id = labels[2]
                    try:
                        card_observacao = card_data["Observações"]
                    except:
                        card_observacao = "Campo em branco"
                    payload = {
                        "query": "mutation { createCard(input: { pipe_id: \"" + pipe_id_MKT_PWR + "\", title: \""+ card_title +"\", fields_attributes:[ {field_id: \"respons_vel\", field_value: \""+card_assignee[0]["id"]+"\"},{field_id: \"o_qu_voc_precisa_fazer\", field_value: \""+ card_ser_feito +"\"}, {field_id:  \"prioridade\", field_value: \""+ label_id +"\"}, {field_id:  \"prazo\", field_value: \"" + card_prazo + "\"}, {field_id:  \"observa_es\", field_value: \"" + card_observacao + "\"}      ]}   ) {     card {       title     }   } }"}
                    response = requests.request("POST", url, json=payload, headers=headers)
                    json_data = json.loads(response.text)
                    print(json_data)
                    print(card_id)
                    return "Webhook received!"
        return "Webhook received!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)