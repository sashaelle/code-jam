using System.Security.Claims;
using CodeJam2026;
using CodeJam2026.Models;
using CodeJam2026.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http.Extensions;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages(options =>
{
    options.Conventions.AuthorizePage("/Team");
    options.Conventions.AuthorizePage("/Judge");
});

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
builder.Services.AddSingleton<ITeamSessionStore, InMemoryTeamSessionStore>();

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

app.Use(async (context, next) =>
{
    if (context.User.Identity?.IsAuthenticated == true &&
        context.User.IsInRole("Team"))
    {
        var name = context.User.FindFirst(ClaimTypes.Name)?.Value;
        var sid = context.User.FindFirst(AuthClaims.AppSessionId)?.Value;

        if (string.IsNullOrWhiteSpace(name) || string.IsNullOrWhiteSpace(sid))
        {
            await context.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);

            if (context.Request.Path.StartsWithSegments("/api", StringComparison.OrdinalIgnoreCase))
            {
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                return;
            }

            context.Response.Redirect("/Login");
            return;
        }

        var store = context.RequestServices.GetRequiredService<ITeamSessionStore>();
        var timeout = TimeSpan.FromSeconds(90);

        if (!store.ValidateSession(name, sid, timeout))
        {
            await context.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);

            if (context.Request.Path.StartsWithSegments("/api", StringComparison.OrdinalIgnoreCase))
            {
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                return;
            }

            context.Response.Redirect("/Login");
            return;
        }

        store.RefreshSession(name, sid);
    }

    await next();
});

app.UseAuthorization();

app.MapRazorPages();
app.MapControllers();

app.Run();
