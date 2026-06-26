import asyncio
import twscrape

async def main():
    api = twscrape.API()
    # Eliminar cuenta vieja y agregar de nuevo con cookies
    await api.pool.delete_accounts('proyinvestigaci')
    await api.pool.add_account(
        username='proyinvestigaci',
        password='proyecto123',
        email='proyectoinvestigacionok@gmail.com',
        email_password='proyecto123',
        cookies='auth_token=2926de437e6844ebd6a60db7a78434eff1256e96; ct0=b2ed3c382011126c054a549b4ebf0c4f351aeec19042adbdd2d8d7d11bc7e3789ed997d8ba534a51051ceb28f025b4a951b467ad8eb8113ce0885173f69de31d410b5381a699aab59e3e08a5146b722f; twid=u%3D2070519802561437696'
    )
    
    # Verificar que funciona
    accounts = await api.pool.get_all()
    for acc in accounts:
        print(f"Usuario: {acc.username} | Activa: {acc.active} | Status: {acc.error_msg}")

asyncio.run(main())