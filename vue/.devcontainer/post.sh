#!/bin/bash

corepack enable

pnpm install
echo apias ppp='pnpm' >> /root/.bashrc 