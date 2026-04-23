using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http.Extensions;
using CodeJam2026.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages(options =>
{
    options.Conventions.AuthorizePage("/Team");
    options.Conventions.AuthorizePage("/Judge");
});

builder.Services.AddSingleton<ITeamSessionStore, InMemoryTeamSessionStore>();

builder.Services
    .AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Login";
        options.AccessDeniedPath = "/Error";
    });

builder.Services.AddAuthorization();
builder.Services.AddControllers();
builder.Services.AddSingleton<ScoreboardVisibilityState>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

var enableHttpsRedirection = app.Configuration.GetValue("EnableHttpsRedirection", !app.Environment.IsDevelopment());
if (enableHttpsRedirection)
{
    app.UseHttpsRedirection();
}

app.Use((ctx, next) =>
{
    if (!ctx.Request.PathBase.HasValue && ctx.Request.Path.StartsWithSegments("/~codejam", out var remaining))
    {
	ctx.Request.PathBase = "/~codejam";
	ctx.Request.Path = remaining;
    }

    return next();
});

app.UseStaticFiles();

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

app.MapRazorPages();
app.MapControllers();

app.Run();
