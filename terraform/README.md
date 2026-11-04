# Terraform — entrepot existant, state a proteger

Le warehouse SIDEFLIX_WH est deja cree par le module du TD 4.2 (X-Small, auto-suspend 60 s, auto-resume). Ne pas le recreer et ne pas lancer apply depuis un state vide.

Le state existant est sur le poste de Jeremy. La reprise v2 demande un backend d’equipe prive, versionne et verrouille comme le guide 09 du pack. Le fichier backend.tf.example adapte son exemple S3, dans le meme cloud AWS eu-west-3. Il n’est pas actif et aucun bucket n’a ete cree par cette preparation.

## Action du detenteur du state

1. Sur le poste contenant le vrai state : verifier l’acces AWS et creer une fois le bucket S3 prive, acces public bloque, versioning actif. Le nom propose doit etre libre ; sinon le remplacer dans l’exemple. Limiter les acces au state et au fichier .tflock. Garder credentials et state hors de Git.
2. Sauvegarder localement le state existant hors du depot. Copier backend.tf.example en backend.tf avec le nom reel du bucket. Authentification AWS au runtime, aucune cle dans HCL.
3. Executer terraform init -migrate-state depuis ce repertoire avec le vrai state ; verifier la migration avant de retirer la copie locale de secours.
4. Executer terraform fmt -check, terraform validate puis terraform plan -detailed-exitcode : attendu No changes/code 0 ; ne pas appliquer si creation/remplacement/destruction proposee. Verifier versioning, verrouillage et acces du backend.
5. Consigner uniquement les resultats non sensibles dans Notion/rendu et partager la configuration validee. Ne pas publier le contenu du state ni les identifiants AWS.

Ce controle n’a pas ete execute sur le poste courant : ni state de Jeremy ni acces AWS disponibles. L’etape 4.2 reste a verifier ; la presence du fichier d’exemple ne prouve pas une migration. La creation initiale du bucket est une etape manuelle du pack, pas une nouvelle architecture de production. Ne pas detruire les ressources avant correction.
