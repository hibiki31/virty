## プロジェクトキック

```bash
mkdir .devcontainer
cat << EOF >> .devcontainer/devcontainer.json
{
  "dockerComposeFile": "compose.yml",
  "service": "golang",
  "workspaceFolder": "/workspace/apigo",
  "customizations": {
		"vscode": {
			"extensions": [
				"golang.go"
			]
		}
	}
}
EOF
cat << EOF >> .devcontainer/compose.yml
services:
  golang:
    image: golang
    volumes:
      - "../../:/workspace:cached"
    stdin_open: true
    tty: true
    ports:
      - 0.0.0.0:8765:8765
  db:
    image: postgres:latest
    restart: unless-stopped
    ports:
      - 0.0.0.0:5432:5432
    volumes:
      - virty-apigo-postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: virty
      POSTGRES_DB: virty
      POSTGRES_PASSWORD: virty-passworde

volumes:
  virty-apigo-postgres-data:
EOF
```

```
go mod init virtygo
go install github.com/labstack/echo/v4
```

```bash
# ファイル名を指定するとファイル分割したファイルすべてを指定する必要あり
go run .
```

## gorm

```bash
go get gorm.io/gorm
go get gorm.io/driver/postgres
```

## 参考

- getとinstall
  - https://zenn.dev/tmk616/articles/383fc3fbb0ec4b

## Air

```
go install github.com/air-verse/air@latest
```