package com.supermercado;

//Abstracción
public abstract class RespuestaBase {
    protected String tipo;

    protected RespuestaBase(String tipo) {
        this.tipo = tipo;
    }

    public String obtenerTipo() {
        return tipo;
    }

    public abstract String obtenerMensaje();
}

