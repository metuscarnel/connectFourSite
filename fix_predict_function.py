#!/usr/bin/env python3
import re

# Lire le fichier
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver la première occurrence de "async function predictAndSimulate()"
start_marker = '        async function predictAndSimulate() {'
end_marker = '        async function importGameFromTxt() {'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Extraire la section à remplacer
    before = content[:start_idx]
    after = content[end_idx:]
    
    # Nouveau code
    new_code = '''        let lastPredictionResult = null;

        async function predictAndSimulate() {
            const movesInput = document.getElementById('importMovesInput');
            const moves = movesInput.value.trim();
            
            if (!moves || !/^\\d+$/.test(moves)) {
                alert('❌ Format invalide! Exemple: 2322786762');
                return;
            }
            
            const resultDiv = document.getElementById('predictionResults');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '⏳ Calcul de la prédiction avec 2 IA Minimax...';
            
            updateStatus('🎮 Simulation en cours...');
            
            try {
                const response = await fetch('/api/predict_and_simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ moves })
                });
                const result = await response.json();
                
                if (result.success) {
                    // Stocker le résultat pour l'animation ultérieure
                    lastPredictionResult = result;
                    
                    // Afficher le résultat + bouton pour voir l'animation
                    resultDiv.innerHTML = `
                        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                            <h2 style="margin: 0 0 15px 0; font-size: 28px;">🎉 ${result.winner} gagne en ${result.remaining_moves} coup${result.remaining_moves > 1 ? 's' : ''} simulé${result.remaining_moves > 1 ? 's' : ''}!</h2>
                            <button onclick="showPredictionAnimation()" style="background: #4CAF50; color: white; border: none; padding: 12px 30px; border-radius: 5px; font-size: 16px; cursor: pointer; transition: 0.3s;">▶️ Voir l'animation</button>
                        </div>
                    `;
                    
                    updateStatus(`✅ Prédiction calculée! ${result.winner} gagne en ${result.remaining_moves} coups.`);
                } else {
                    resultDiv.innerHTML = `❌ ${result.error}`;
                    updateStatus(`❌ ${result.error}`);
                }
            } catch (e) {
                console.error(e);
                resultDiv.innerHTML = `❌ Erreur: ${e.message}`;
                updateStatus('❌ Erreur réseau');
            }
        }

        async function showPredictionAnimation() {
            if (!lastPredictionResult) return;
            
            const result = lastPredictionResult;
            const resultDiv = document.getElementById('predictionResults');
            resultDiv.innerHTML = '⏳ Affichage de l\'animation...';
            
            // Séparer coups importés et simulés
            const initialMoves = result.all_moves.substring(0, result.initial_moves);
            const simulatedMoves = result.all_moves.substring(result.initial_moves);
            
            // Afficher avec animation
            await displayBoardWithMovesAnimated(initialMoves, simulatedMoves, result.winning_positions);
            
            // Re-afficher le résultat et le bouton après animation
            resultDiv.innerHTML = `
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                    <h2 style="margin: 0; font-size: 28px;">🎉 ${result.winner} gagne en ${result.remaining_moves} coup${result.remaining_moves > 1 ? 's' : ''} simulé${result.remaining_moves > 1 ? 's' : ''}!</h2>
                </div>
            `;
            
            updateStatus(`🎉 Animation terminée! ${result.winner} gagne en ${result.remaining_moves} coups.`);
        }

'''
    
    # Assembler le nouveau contenu
    new_content = before + new_code + after
    
    # Écrire le fichier
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fichier modifié avec succès!")
    print(f"   - Supprimé/remplacé de {start_idx} à {end_idx}")
else:
    print("❌ Marqueurs non trouvés!")
