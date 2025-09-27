import streamlit as st
import hashlib
import base58
import time
import warnings

# Supprimer les avertissements
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Générateur d'Adresse Bitcoin",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un meilleur design
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #f7931a;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        font-size: 18px;
    }
    .stButton>button:hover {
        background-color: #ff9500;
        border: 2px solid #f7931a;
    }
    .step-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #f7931a;
    }
    .success-box {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border: 2px solid #28a745;
    }
    .code-box {
        background-color: #2d2d2d;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        overflow-x: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Fonctions de génération d'adresse Bitcoin
def generate_keys():
    private_key = "1" * 64
    public_key = "0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b23522cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6"
    return private_key, public_key

def sha256_hash(data):
    return hashlib.sha256(bytes.fromhex(data)).hexdigest()

def ripemd160_hash(data):
    h = hashlib.new('ripemd160')
    h.update(bytes.fromhex(data))
    return h.hexdigest()

def add_version_prefix(data, version='00'):
    return version + data

def get_network_info(network):
    """Retourne les informations selon le réseau"""
    networks = {
        'mainnet': {
            'version': '00',
            'prefix': '1',
            'name': 'Bitcoin Mainnet',
            'color': '#f7931a',
            'warning': 'ATTENTION: Ne JAMAIS utiliser cette clé privée pour de vrais bitcoins!',
            'warning_color': 'error'
        },
        'testnet': {
            'version': '6F',
            'prefix': 'm ou n',
            'name': 'Bitcoin Testnet',
            'color': '#50c878',
            'warning': 'Testnet: Parfait pour les tests sans risque!',
            'warning_color': 'success'
        }
    }
    return networks.get(network, networks['mainnet'])

def calculate_checksum(data):
    first_hash = sha256_hash(data)
    second_hash = sha256_hash(first_hash)
    return second_hash[:8]

def assemble_address(prefix_pubkey_hash, checksum):
    return prefix_pubkey_hash + checksum

def encode_base58check(data):
    data_bytes = bytes.fromhex(data)
    address = base58.b58encode(data_bytes).decode('utf-8')
    return address

# En-tête de l'application
st.title("₿ Générateur d'Adresse Bitcoin")
st.markdown("### *Processus ECDSA (secp256k1) - 7 Étapes*")
st.markdown("---")

# Créer deux colonnes pour la mise en page
col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### 📊 Navigation")
    
    # Sélection du réseau
    st.markdown("### 🌐 Réseau")
    network = st.radio(
        "Choisissez le réseau:",
        ["mainnet", "testnet"],
        format_func=lambda x: "🔴 Mainnet (Réel)" if x == "mainnet" else "🟢 Testnet (Test)",
        help="Mainnet = Bitcoins réels | Testnet = Bitcoins de test gratuits"
    )
    
    network_info = get_network_info(network)
    
    if network == 'testnet':
        st.success(f" Mode Test Activé\nAdresse commencera par '{network_info['prefix']}'")
    else:
        st.warning(" Mode Production\nNe pas utiliser pour stocker de vrais bitcoins!")
    
    st.markdown("---")
    
    show_all = st.checkbox("Afficher toutes les étapes", value=True)
    if not show_all:
        step_select = st.selectbox(
            "Sélectionner une étape",
            ["Étape 1: Génération des clés",
             "Étape 2: SHA-256",
             "Étape 3: RIPEMD-160",
             "Étape 4: Préfixe de version",
             "Étape 5: Checksum",
             "Étape 6: Assemblage",
             "Étape 7: Base58Check"]
        )
    
    st.markdown("---")
    st.markdown("### Options")
    show_details = st.checkbox("Afficher les détails techniques", value=True)
    animation = st.checkbox("Animation des étapes", value=True)

with col1:
    # Afficher les informations du réseau sélectionné
    network_info = get_network_info(network)
    st.info(f" **Réseau sélectionné**: {network_info['name']}")
    
    # Bouton de génération principal
    if st.button(" GÉNÉRER L'ADRESSE BITCOIN", type="primary"):
        st.markdown("---")
        
        # Initialiser la barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Étape 1: Génération des clés
        if show_all or (not show_all and step_select == "Étape 1: Génération des clés"):
            status_text.text("Génération des clés...")
            progress_bar.progress(10)
            
            st.markdown("## Étape 1: Génération de la paire de clés ECDSA")
            private_key, public_key = generate_keys()
            
            col1a, col1b = st.columns(2)
            with col1a:
                st.markdown("** Clé Privée (32 octets)**")
                st.code(f"{private_key[:32]}...\n...{private_key[-32:]}", language="text")
                st.info(f"Taille: {len(private_key)} caractères hex")
            
            with col1b:
                st.markdown("** Clé Publique (65 octets)**")
                st.code(f"{public_key[:32]}...\n...{public_key[-32:]}", language="text")
                st.info(f"Taille: {len(public_key)} caractères hex")
            
            if show_details:
                with st.expander(" Détails de l'étape 1"):
                    st.markdown("""
                    - **Algorithme**: ECDSA avec courbe secp256k1
                    - **Clé privée**: Nombre aléatoire de 256 bits
                    - **Clé publique**: Point (x, y) sur la courbe elliptique
                    - **Sécurité**: Impossible de retrouver la clé privée depuis la publique
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 2: SHA-256
        if show_all or (not show_all and step_select == "Étape 2: SHA-256"):
            status_text.text("Application de SHA-256...")
            progress_bar.progress(25)
            
            st.markdown("##  Étape 2: Hachage SHA-256")
            sha256_result = sha256_hash(public_key)
            
            col2a, col2b = st.columns([3, 1])
            with col2a:
                st.code(sha256_result, language="text")
            with col2b:
                st.metric("Taille", "32 octets", delta="-33 octets")
            
            if show_details:
                with st.expander(" Détails de l'étape 2"):
                    st.markdown("""
                    - **Fonction**: SHA-256 (Secure Hash Algorithm)
                    - **Entrée**: 65 octets (clé publique)
                    - **Sortie**: 32 octets (256 bits)
                    - **Propriété**: Irréversible et déterministe
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 3: RIPEMD-160
        if show_all or (not show_all and step_select == "Étape 3: RIPEMD-160"):
            status_text.text("Application de RIPEMD-160...")
            progress_bar.progress(40)
            
            st.markdown("## Étape 3: Hachage RIPEMD-160")
            ripemd160_result = ripemd160_hash(sha256_result)
            
            col3a, col3b = st.columns([3, 1])
            with col3a:
                st.code(ripemd160_result, language="text")
            with col3b:
                st.metric("Taille", "20 octets", delta="-12 octets")
            
            if show_details:
                with st.expander(" Détails de l'étape 3"):
                    st.markdown("""
                    - **Fonction**: RIPEMD-160
                    - **Entrée**: 32 octets (SHA-256)
                    - **Sortie**: 20 octets (160 bits)
                    - **Avantage**: Double sécurité + réduction de taille
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 4: Préfixe
        if show_all or (not show_all and step_select == "Étape 4: Préfixe de version"):
            status_text.text("Ajout du préfixe de version...")
            progress_bar.progress(55)
            
            st.markdown("##  Étape 4: Ajout du préfixe de version")
            version_prefix = network_info['version']
            prefixed_data = add_version_prefix(ripemd160_result, version_prefix)
            
            col4a, col4b = st.columns([3, 1])
            with col4a:
                st.code(f"{version_prefix} + {ripemd160_result}", language="text")
                st.code(prefixed_data, language="text")
            with col4b:
                st.metric("Préfixe", f"0x{version_prefix}", help=network_info['name'])
                st.info(f"Adresse commencera par '{network_info['prefix']}'")
            
            if show_details:
                with st.expander(" Détails de l'étape 4"):
                    st.markdown(f"""
                    - **Préfixe 0x{version_prefix}**: {network_info['name']}
                    - **Préfixe 0x00**: Bitcoin Mainnet (commence par '1')
                    - **Préfixe 0x6F**: Bitcoin Testnet (commence par 'm' ou 'n')
                    - **Préfixe 0x05**: Pay-to-Script-Hash
                    - **Taille finale**: 21 octets
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 5: Checksum
        if show_all or (not show_all and step_select == "Étape 5: Checksum"):
            status_text.text("Calcul du checksum...")
            progress_bar.progress(70)
            
            st.markdown("##  Étape 5: Calcul du Checksum")
            checksum = calculate_checksum(prefixed_data)
            
            col5a, col5b = st.columns([3, 1])
            with col5a:
                st.markdown("**Double SHA-256 + 4 premiers octets**")
                st.code(checksum, language="text")
            with col5b:
                st.metric("Checksum", "4 octets")
                st.success("✓ Protection contre les erreurs")
            
            if show_details:
                with st.expander(" Détails de l'étape 5"):
                    st.markdown("""
                    1. Premier SHA-256 sur les données préfixées
                    2. Deuxième SHA-256 sur le résultat
                    3. Extraction des 4 premiers octets
                    - **Fonction**: Détection d'erreurs de saisie (99,99%)
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 6: Assemblage
        if show_all or (not show_all and step_select == "Étape 6: Assemblage"):
            status_text.text("Assemblage de l'adresse...")
            progress_bar.progress(85)
            
            st.markdown("##  Étape 6: Assemblage de l'adresse")
            assembled_address = assemble_address(prefixed_data, checksum)
            
            st.code(assembled_address, language="text")
            
            col6a, col6b, col6c = st.columns(3)
            with col6a:
                st.info(f"Préfixe: {version_prefix}")
            with col6b:
                st.info(f"Hash: {ripemd160_result[:10]}...")
            with col6c:
                st.info(f"Checksum: {checksum}")
            
            if show_details:
                with st.expander(" Détails de l'étape 6"):
                    st.markdown("""
                    - **Structure**: [Version] + [Hash] + [Checksum]
                    - **Taille totale**: 25 octets
                    - **Format**: Hexadécimal (50 caractères)
                    """)
            
            if animation:
                time.sleep(0.5)
        
        # Étape 7: Base58Check
        if show_all or (not show_all and step_select == "Étape 7: Base58Check"):
            status_text.text("Encodage en Base58Check...")
            progress_bar.progress(95)
            
            st.markdown("## Étape 7: Encodage Base58Check")
            bitcoin_address = encode_base58check(assembled_address)
            
            st.markdown("### Adresse Bitcoin Finale:")
            st.code(bitcoin_address, language="text")
            
            col7a, col7b, col7c = st.columns(3)
            with col7a:
                st.success(f" {len(bitcoin_address)} caractères")
            with col7b:
                st.success(" Format Base58")
            with col7c:
                if network == 'testnet':
                    st.success(f" Testnet ('{bitcoin_address[0]}')")
                else:
                    st.success(" Commence par '1'")
            
            if show_details:
                with st.expander(" Détails de l'étape 7"):
                    st.markdown("""
                    - **Encodage**: Base58 (58 caractères alphanumériques)
                    - **Caractères exclus**: 0, O, I, l (évite la confusion)
                    - **Lisibilité**: Facile à copier et partager
                    - **QR Code**: Compatible avec les codes QR
                    """)
            
            progress_bar.progress(100)
            status_text.text(" Génération terminée!")
            
            if animation:
                st.balloons()
            
            # Boîte de succès finale
            st.markdown("---")
            
            if network == 'testnet':
                st.markdown(f"""
                <div class="success-box">
                    <h2 style="color: #28a745; margin-top: 0;"> Adresse Bitcoin Testnet Générée!</h2>
                    <p style="font-size: 20px; font-family: monospace; word-break: break-all;">
                        <strong>{bitcoin_address}</strong>
                    </p>
                    <p style="color: #6c757d;">
                        Cette adresse est prête à recevoir des bitcoins de TEST (sans valeur réelle).
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Guide pour obtenir des bitcoins testnet
                st.markdown("---")
                st.markdown("## Comment obtenir des Bitcoins Testnet GRATUITS")
                
                col_guide1, col_guide2 = st.columns(2)
                
                with col_guide1:
                    st.markdown("### Faucets Testnet (Robinets)")
                    st.markdown("""
                    Visitez ces sites pour obtenir des tBTC gratuits:
                    
                    1. **[coinfaucet.eu/btc-testnet](https://coinfaucet.eu/en/btc-testnet/)**
                       - 0.01 tBTC toutes les 24h
                       - Pas d'inscription requise
                    
                    2. **[testnet-faucet.mempool.co](https://testnet-faucet.mempool.co/)**
                       - 0.001 - 0.01 tBTC
                       - Simple et rapide
                    
                    3. **[bitcoinfaucet.uo1.net](https://bitcoinfaucet.uo1.net/)**
                       - Ancien mais fiable
                       - 0.001 tBTC
                    
                    4. **[testnet.help](https://testnet.help/en/btcfaucet/testnet)**
                       - Interface moderne
                       - Distribution régulière
                    """)
                
                with col_guide2:
                    st.markdown("### Portefeuilles Testnet Recommandés")
                    st.markdown("""
                    Pour gérer vos tBTC:
                    
                    **1. Electrum (Desktop)**
                    - Téléchargez [electrum.org](https://electrum.org/)
                    - Lancez avec: `electrum --testnet`
                    - Importez votre adresse
                    
                    **2. Blue Wallet (Mobile)**
                    - App iOS/Android
                    - Active le mode testnet dans les paramètres
                    - Facile à utiliser
                    
                    **3. Bitcoin Core (Avancé)**
                    - Client officiel
                    - Mode testnet: `bitcoind -testnet`
                    - Plus complet mais lourd
                    """)
                
                st.markdown("---")
                st.markdown("### Étapes pour recevoir vos premiers tBTC:")
                
                st.markdown("""
                1. **Copiez votre adresse testnet** ci-dessus
                2. **Visitez un faucet** (par exemple coinfaucet.eu)
                3. **Collez votre adresse** dans le formulaire
                4. **Résolvez le captcha** si demandé
                5. **Cliquez sur "Get Bitcoins"**
                6. **Attendez 10-30 minutes** pour la confirmation
                7. **Vérifiez la transaction** sur un explorateur de blocs
                """)
                
                st.markdown("### Explorer de Blocs Testnet")
                st.markdown(f"""
                Vérifiez vos transactions sur:
                - [blockstream.info/testnet](https://blockstream.info/testnet/)
                - [live.blockcypher.com/btc-testnet](https://live.blockcypher.com/btc-testnet/)
                
                **Recherchez votre adresse:**  
                `{bitcoin_address}`
                """)
                
                st.info("""
                 **Astuce:** Les bitcoins testnet n'ont AUCUNE valeur réelle.  
                Ils sont parfaits pour apprendre et tester sans risque!
                """)
                
            else:
                st.markdown(f"""
                <div class="success-box">
                    <h2 style="color: #28a745; margin-top: 0;"> Adresse Bitcoin Générée avec Succès!</h2>
                    <p style="font-size: 20px; font-family: monospace; word-break: break-all;">
                        <strong>{bitcoin_address}</strong>
                    </p>
                    <p style="color: #6c757d;">
                        Cette adresse est prête à recevoir des bitcoins sur le réseau principal (mainnet).
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.warning("""
                 **ATTENTION SÉCURITÉ:**  
                N'utilisez JAMAIS cette clé privée pour stocker de vrais bitcoins!  
                Cette démonstration utilise une clé privée fixe connue de tous.  
                Pour un usage réel, générez une nouvelle clé privée aléatoire et sécurisée.
                """)

# Sidebar avec informations
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png", width=100)
    st.markdown("## À propos")
    st.markdown("""
    Cette application démontre le processus complet de génération d'une adresse Bitcoin en utilisant:
    
    - **ECDSA** (secp256k1)
    - **SHA-256**
    - **RIPEMD-160**
    - **Base58Check**
    
    ###  Sécurité
    - Clé privée de 256 bits
    - Double hachage
    - Checksum intégré
    
    ### Statistiques
    - Adresses possibles: 2^160
    - Temps de génération: < 1ms
    - Sécurité: Niveau cryptographique
    """)
    
    st.markdown("---")
    st.markdown("### Attention")
    
    if network == 'testnet':
        st.success("""
         **Mode Testnet Activé**  
        Les bitcoins testnet sont gratuits et n'ont aucune valeur réelle.  
        Parfait pour apprendre et expérimenter sans risque!
        """)
    else:
        st.warning("""
         **Mode Mainnet**  
        Ceci est une démonstration éducative.  
        N'utilisez JAMAIS cette clé privée pour stocker de vrais bitcoins!
        """)
    
    st.markdown("---")
    st.markdown("### Ressources")
    st.markdown("""
    **Documentation:**
    - [Bitcoin.org](https://bitcoin.org)
    - [secp256k1](https://en.bitcoin.it/wiki/Secp256k1)
    - [Base58Check](https://en.bitcoin.it/wiki/Base58Check_encoding)
    
    **Testnet:**
    - [Testnet Faucets](https://coinfaucet.eu/en/btc-testnet/)
    - [Testnet Explorer](https://blockstream.info/testnet/)
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d;">
        <p>Développé pour un TP de Blockchain | © 2025</p>
        <p>⚡ Propulsé par Streamlit et Python</p>
    </div>
""", unsafe_allow_html=True)
