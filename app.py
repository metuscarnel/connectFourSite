from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Puissance 4 IA - Coming Soon</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: white;
            }
            
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            p {
                font-size: 1.3em;
                margin-bottom: 40px;
                opacity: 0.95;
            }
            
            .spinner {
                width: 60px;
                height: 60px;
                margin: 0 auto;
                border: 6px solid rgba(255, 255, 255, 0.3);
                border-top: 6px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @media (max-width: 600px) {
                h1 {
                    font-size: 2em;
                }
                p {
                    font-size: 1em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Projet Puissance 4 IA 🤖</h1>
            <p>Le jeu est en cours de déploiement. Arrivée imminente !</p>
            <div class="spinner"></div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
