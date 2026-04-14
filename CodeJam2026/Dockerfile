# ---------- BUILD STAGE ----------
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY CodeJam2026.csproj ./
RUN dotnet restore

# Copy everything else
COPY . ./
RUN dotnet publish CodeJam2026.csproj -c Release -o /app/publish

# ---------- RUNTIME STAGE ----------
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app

# Install native dependency used by Npgsql on Linux
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

# Set container HTTP port
ENV ASPNETCORE_HTTP_PORTS=80

# Copy built app
COPY --from=build /app/publish .

# Expose port
EXPOSE 80

# Run app
ENTRYPOINT ["dotnet", "CodeJam2026.dll"]
