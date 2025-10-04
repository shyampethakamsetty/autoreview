FROM node:20-alpine
WORKDIR /app

# Accept build arguments for environment variables
ARG VITE_API_URL
ARG VITE_API_BASE_URL
ARG VITE_API_KEY

# Set them as environment variables for the build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL  
ENV VITE_API_KEY=$VITE_API_KEY

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm i -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
