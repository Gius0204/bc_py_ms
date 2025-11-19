"""
Script de prueba para sincronización con HubSpot
Ejecutar con: python test_sync.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.hubspot_api import sincronizar_empresa_a_hubspot, sincronizar_contacto_a_hubspot

def test_sync_empresa():
    """Prueba sincronización de una empresa"""
    print("\n" + "="*60)
    print("PROBANDO SINCRONIZACIÓN DE EMPRESA")
    print("="*60)
    
    # Datos de prueba de una empresa
    empresa_test = {
        "id": 999,  # ID de prueba
        "name": "Empresa de Prueba Sync",
        "country": "México",
        "sector": "Tecnologías de la Información",
        "total_revenue": 500000.50,
        "net_profit": 125000.75,
        "lead_status": "Nuevo",  # Se mapeará a "NEW"
        "hubspot_id": None  # Simular primera sincronización
    }
    
    print("\nDatos a sincronizar:")
    print(f"  - Nombre: {empresa_test['name']}")
    print(f"  - País: {empresa_test['country']}")
    print(f"  - Sector: {empresa_test['sector']}")
    print(f"  - Ingresos: ${empresa_test['total_revenue']:,.2f}")
    print(f"  - Ganancia neta: ${empresa_test['net_profit']:,.2f}")
    print(f"  - Lead Status: {empresa_test['lead_status']} (se enviará como 'NEW')")
    print(f"  - HubSpot ID actual: {empresa_test['hubspot_id']}")
    
    try:
        print("\nEnviando a HubSpot...")
        resultado = sincronizar_empresa_a_hubspot(empresa_test)
        
        print("\n✅ SINCRONIZACIÓN EXITOSA!")
        print(f"  - Acción: {resultado['action']}")
        print(f"  - HubSpot ID retornado: {resultado['hubspot_id']}")
        print(f"\n  👉 Guarda este ID para la próxima prueba de actualización")
        
        return resultado['hubspot_id']
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None


def test_sync_contacto(company_hubspot_id=None):
    """Prueba sincronización de un contacto"""
    print("\n" + "="*60)
    print("PROBANDO SINCRONIZACIÓN DE CONTACTO")
    print("="*60)
    
    # Datos de prueba de un contacto
    contacto_test = {
        "id": 888,  # ID de prueba
        "nombre": "Juan Pérez Test",
        "first_name": "Juan",
        "last_name": "Pérez Test",
        "email": "juan.perez.test@example.com",
        "telefono": "+521234567890",
        "cargo": "Director de Pruebas",
        "country": "México",
        "estado": "Nuevo",  # Se mapeará a "NEW"
        "company_id": 1,
        "hubspot_id": None  # Simular primera sincronización
    }
    
    print("\nDatos a sincronizar:")
    print(f"  - Nombre: {contacto_test['first_name']} {contacto_test['last_name']}")
    print(f"  - Email: {contacto_test['email']}")
    print(f"  - Teléfono: {contacto_test['telefono']}")
    print(f"  - Cargo: {contacto_test['cargo']}")
    print(f"  - País: {contacto_test['country']}")
    print(f"  - Estado: {contacto_test['estado']} (se enviará como 'NEW')")
    print(f"  - HubSpot ID actual: {contacto_test['hubspot_id']}")
    if company_hubspot_id:
        print(f"  - Se asociará con empresa HubSpot ID: {company_hubspot_id}")
    
    try:
        print("\nEnviando a HubSpot...")
        resultado = sincronizar_contacto_a_hubspot(contacto_test, company_hubspot_id)
        
        print("\n✅ SINCRONIZACIÓN EXITOSA!")
        print(f"  - Acción: {resultado['action']}")
        print(f"  - HubSpot ID retornado: {resultado['hubspot_id']}")
        print(f"\n  👉 Guarda este ID para la próxima prueba de actualización")
        
        return resultado['hubspot_id']
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None


def test_update_empresa(hubspot_id):
    """Prueba actualización de una empresa existente"""
    print("\n" + "="*60)
    print("PROBANDO ACTUALIZACIÓN DE EMPRESA")
    print("="*60)
    
    empresa_update = {
        "id": 999,
        "name": "Empresa de Prueba Sync ACTUALIZADA",
        "country": "Perú",  # Cambio
        "sector": "Turismo",  # Cambio
        "total_revenue": 750000.00,  # Cambio
        "net_profit": 200000.00,  # Cambio
        "lead_status": "Abierto",  # Cambio
        "hubspot_id": hubspot_id  # Ahora tiene ID
    }
    
    print(f"\nActualizando empresa con HubSpot ID: {hubspot_id}")
    print("Nuevos datos:")
    print(f"  - Nombre: {empresa_update['name']}")
    print(f"  - País: {empresa_update['country']}")
    print(f"  - Sector: {empresa_update['sector']}")
    print(f"  - Ingresos: ${empresa_update['total_revenue']:,.2f}")
    print(f"  - Ganancia neta: ${empresa_update['net_profit']:,.2f}")
    print(f"  - Lead Status: {empresa_update['lead_status']}")
    
    try:
        print("\nActualizando en HubSpot...")
        resultado = sincronizar_empresa_a_hubspot(empresa_update)
        
        print("\n✅ ACTUALIZACIÓN EXITOSA!")
        print(f"  - Acción: {resultado['action']}")
        print(f"  - HubSpot ID: {resultado['hubspot_id']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_update_contacto(hubspot_id, company_hubspot_id=None):
    """Prueba actualización de un contacto existente"""
    print("\n" + "="*60)
    print("PROBANDO ACTUALIZACIÓN DE CONTACTO")
    print("="*60)
    
    contacto_update = {
        "id": 888,
        "first_name": "Juan Carlos",  # Cambio
        "last_name": "Pérez García",  # Cambio
        "email": "jc.perez@example.com",  # Cambio
        "telefono": "+529876543210",  # Cambio
        "cargo": "CEO",  # Cambio
        "country": "Perú",  # Cambio
        "estado": "Conectado",  # Cambio
        "hubspot_id": hubspot_id  # Ahora tiene ID
    }
    
    print(f"\nActualizando contacto con HubSpot ID: {hubspot_id}")
    print("Nuevos datos:")
    print(f"  - Nombre: {contacto_update['first_name']} {contacto_update['last_name']}")
    print(f"  - Email: {contacto_update['email']}")
    print(f"  - Teléfono: {contacto_update['telefono']}")
    print(f"  - Cargo: {contacto_update['cargo']}")
    print(f"  - País: {contacto_update['country']}")
    print(f"  - Estado: {contacto_update['estado']}")
    if company_hubspot_id:
        print(f"  - Asociar con empresa ID: {company_hubspot_id}")
    
    try:
        print("\nActualizando en HubSpot...")
        resultado = sincronizar_contacto_a_hubspot(contacto_update, company_hubspot_id)
        
        print("\n✅ ACTUALIZACIÓN EXITOSA!")
        print(f"  - Acción: {resultado['action']}")
        print(f"  - HubSpot ID: {resultado['hubspot_id']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("\n🔧 PRUEBAS DE SINCRONIZACIÓN CON HUBSPOT")
    print("="*60)
    
    # Menú de opciones
    print("\nOpciones:")
    print("1. Crear nueva empresa en HubSpot")
    print("2. Crear nuevo contacto en HubSpot")
    print("3. Actualizar empresa existente (necesitas HubSpot ID)")
    print("4. Actualizar contacto existente (necesitas HubSpot ID)")
    print("5. Ejecutar todas las pruebas (crear empresa y contacto)")
    
    opcion = input("\nElige una opción (1-5): ").strip()
    
    if opcion == "1":
        test_sync_empresa()
    
    elif opcion == "2":
        usar_empresa = input("¿Asociar con una empresa? (s/n): ").strip().lower()
        company_id = None
        if usar_empresa == "s":
            company_id = input("Ingresa el HubSpot ID de la empresa: ").strip()
        test_sync_contacto(company_id)
    
    elif opcion == "3":
        hubspot_id = input("Ingresa el HubSpot ID de la empresa a actualizar: ").strip()
        test_update_empresa(hubspot_id)
    
    elif opcion == "4":
        hubspot_id = input("Ingresa el HubSpot ID del contacto a actualizar: ").strip()
        usar_empresa = input("¿Asociar/actualizar asociación con una empresa? (s/n): ").strip().lower()
        company_id = None
        if usar_empresa == "s":
            company_id = input("Ingresa el HubSpot ID de la empresa: ").strip()
        test_update_contacto(hubspot_id, company_id)
    
    elif opcion == "5":
        # Ejecutar todo
        empresa_id = test_sync_empresa()
        
        if empresa_id:
            input("\nPresiona ENTER para continuar con el contacto...")
            test_sync_contacto(empresa_id)
    
    else:
        print("Opción inválida")
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)
    print("\nPuedes verificar los registros en HubSpot:")
    print("https://app.hubspot.com/contacts/")
    print("\n")
