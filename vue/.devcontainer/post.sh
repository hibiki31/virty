#!/bin/bash

corepack enable

pnpm install
echo alias ppp='pnpm' >> /root/.bashrc 