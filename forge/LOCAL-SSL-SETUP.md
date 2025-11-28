# Configuration SSL Local avec mkcert pour axoiq.com

Ce guide explique comment accéder à vos applications via `https://*.axoiq.com` **localement** sans warnings SSL.

## 🎯 Objectif

- Accéder à `https://nexus.axoiq.com`, `https://synapse.axoiq.com`, etc.
- SSL valide (pas de warning dans le navigateur)
- 100% local (pas de DNS public, pas de Cloudflare Tunnel)
- Un seul certificat wildcard pour tous les sous-domaines

---

## 📋 Prérequis

### 1. Installer mkcert

**Avec Chocolatey:**
```powershell
choco install mkcert
```

**Avec Scoop:**
```powershell
scoop bucket add extras
scoop install mkcert
```

**Vérifier l'installation:**
```powershell
mkcert -version
```

---

## 🚀 Procédure Complète

### Étape 1: Modifier le fichier hosts

**IMPORTANT:** Exécuter en tant qu'Administrateur

```powershell
# Clic droit > Exécuter en tant qu'administrateur
.\setup-local-domains.ps1
```

Ce script ajoute ces entrées à `C:\Windows\System32\drivers\etc\hosts`:
```
127.0.0.1    nexus.axoiq.com
127.0.0.1    api-nexus.axoiq.com
127.0.0.1    synapse.axoiq.com
127.0.0.1    api.axoiq.com
127.0.0.1    portal.axoiq.com
127.0.0.1    grafana.axoiq.com
127.0.0.1    loki.axoiq.com
127.0.0.1    pgadmin.axoiq.com
127.0.0.1    prisma.axoiq.com
```

---

### Étape 2: Générer les certificats SSL

```powershell
.\generate-ssl-certs.ps1
```

Ce script:
1. Installe la CA locale dans Windows (une seule fois)
2. Génère un certificat wildcard pour `*.axoiq.com`
3. Sauvegarde les fichiers dans `config/traefik/`:
   - `axoiq.com.crt` (certificat)
   - `axoiq.com.key` (clé privée)

---

### Étape 3: Redémarrer Traefik

```powershell
docker restart workspace-traefik
```

Attendre 10 secondes que Traefik charge les nouveaux certificats.

---

### Étape 4: Tester l'accès HTTPS

Ouvrir dans votre navigateur:
- ✅ https://nexus.axoiq.com
- ✅ https://synapse.axoiq.com
- ✅ https://portal.axoiq.com
- ✅ https://grafana.axoiq.com

**Résultat attendu:** 🔒 Cadenas vert, pas de warning SSL!

---

## 🔧 Dépannage

### Le navigateur affiche toujours un warning SSL

**1. Vérifier que mkcert CA est installée:**
```powershell
mkcert -install
```

**2. Vérifier les certificats:**
```powershell
ls D:\Projects\EPCB-Tools\workspace\config\traefik\*.crt
ls D:\Projects\EPCB-Tools\workspace\config\traefik\*.key
```

**3. Redémarrer Traefik:**
```powershell
docker restart workspace-traefik
docker logs workspace-traefik --tail 50
```

**4. Vider le cache du navigateur:**
- Chrome: `Ctrl+Shift+Delete` > Effacer les données de navigation
- Edge: `Ctrl+Shift+Delete` > Effacer les données de navigation

---

### "This site can't be reached"

**1. Vérifier le fichier hosts:**
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Assurez-vous que les entrées `*.axoiq.com` sont présentes.

**2. Tester la résolution DNS:**
```powershell
ping nexus.axoiq.com
# Devrait répondre 127.0.0.1
```

**3. Vérifier que Traefik est lancé:**
```powershell
docker ps | findstr traefik
```

---

### Traefik ne charge pas les certificats

**1. Vérifier les logs:**
```powershell
docker logs workspace-traefik --tail 100 | findstr -i "certificate\|tls\|error"
```

**2. Vérifier les permissions:**
Les fichiers `.crt` et `.key` doivent être lisibles par Docker.

**3. Vérifier le chemin dans certificates.yml:**
```yaml
tls:
  certificates:
    - certFile: /etc/traefik/dynamic/axoiq.com.crt
      keyFile: /etc/traefik/dynamic/axoiq.com.key
```

---

## 📝 Fichiers Modifiés

```
D:\Projects\EPCB-Tools\workspace\
├── .env                              # DOMAIN=axoiq.com
├── config/traefik/
│   ├── dynamic.yml                   # Routes HTTPS pour *.axoiq.com
│   ├── certificates.yml              # Configuration SSL
│   ├── axoiq.com.crt                 # Certificat (généré)
│   └── axoiq.com.key                 # Clé privée (généré)
├── setup-local-domains.ps1           # Script hosts file
├── generate-ssl-certs.ps1            # Script certificats
└── LOCAL-SSL-SETUP.md                # Ce fichier

C:\Windows\System32\drivers\etc\hosts # Entrées DNS locales
```

---

## 🌐 URLs Disponibles

| Service | URL Locale | URL Production (future) |
|---------|-----------|-------------------------|
| Nexus Frontend | https://nexus.axoiq.com | https://nexus.axoiq.com |
| Nexus Backend | https://api-nexus.axoiq.com | https://api-nexus.axoiq.com |
| Synapse Frontend | https://synapse.axoiq.com | https://synapse.axoiq.com |
| Synapse Backend | https://api.axoiq.com | https://api.axoiq.com |
| Portal | https://portal.axoiq.com | https://portal.axoiq.com |
| Grafana | https://grafana.axoiq.com | https://grafana.axoiq.com |
| pgAdmin | https://pgadmin.axoiq.com | https://pgadmin.axoiq.com |
| Prisma Studio | https://prisma.axoiq.com | https://prisma.axoiq.com |

---

## ✨ Avantages de cette approche

✅ **SSL valide** - Pas de warning "Not Secure"
✅ **100% local** - Pas de configuration DNS publique
✅ **Pas de Cloudflare Tunnel** - Pas besoin de règles de proxy
✅ **Wildcard certificate** - Un seul certificat pour tous les sous-domaines
✅ **Même domaine dev/prod** - Facilite les tests et déploiements
✅ **Révocation facile** - `mkcert -uninstall` pour tout supprimer

---

## 🔄 Migration vers Production

Quand vous serez prêt à exposer publiquement:

1. **Configurer Cloudflare DNS:**
   - Pointer `*.axoiq.com` vers votre IP publique
   - Activer Cloudflare Proxy (orange cloud)

2. **Modifier Traefik pour Let's Encrypt:**
   ```yaml
   # Dans dynamic.yml, remplacer:
   tls: {}
   # Par:
   tls:
     certResolver: letsencrypt
   ```

3. **Supprimer les entrées hosts locales**

4. **Let's Encrypt générera automatiquement** les certificats SSL publics

---

## 🛡️ Sécurité

- Les certificats mkcert sont **valides seulement sur votre machine**
- Personne d'autre ne peut voir votre site comme "sécurisé"
- Parfait pour développement local
- Pour production publique, utilisez Let's Encrypt

---

**Dernière mise à jour:** 2025-11-27
**Contact:** EPCB Workspace Team
