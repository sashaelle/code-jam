# ---------- BUILD STAGE ----------
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY InvestorPrototype.csproj ./
RUN dotnet restore

# Copy everything else
COPY . ./
RUN dotnet publish -c Release -o /app/publish

# ---------- RUNTIME STAGE ----------
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Set environment + port
ENV ASPNETCORE_URLS=http://+:80

# Copy built app
COPY --from=build /app/publish .

# Expose port
EXPOSE 80

# Run app
ENTRYPOINT ["dotnet", "InvestorPrototype.dll"]
