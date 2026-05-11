FROM node:22-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Run the development server and bind to all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
