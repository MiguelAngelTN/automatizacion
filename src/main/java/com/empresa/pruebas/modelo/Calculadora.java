package com.empresa.pruebas.modelo;


public class Calculadora {

    /**
     * Suma dos valores.
     *
     * @param a primer operando
     * @param b segundo operando
     * @return la suma de a + b
     */
    public double suma(double a, double b) {
        return a + b;
    }

    /**
     * Resta dos valores.
     *
     * @param a minuendo
     * @param b sustraendo
     * @return la diferencia a - b
     */
    public double resta(double a, double b) {
        return a - b;
    }

    /**
     * Multiplica dos valores.
     *
     * @param a primer factor
     * @param b segundo factor
     * @return el producto a * b
     */
    public double multiplicacion(double a, double b) {
        return a * b;
    }

    /**
     * Divide dos valores.
     *
     * @param a dividendo
     * @param b divisor
     * @return el cociente a / b
     * @throws IllegalArgumentException si el divisor es cero (precondicion invalida)
     */
    public double division(double a, double b) {
        if (b == 0.0d) {
            throw new IllegalArgumentException("No se puede dividir por cero");
        }
        return a / b;
    }

    /**
     * Indica si un numero es par.
     *
     * @param valor numero a evaluar
     * @return true si el valor es par
     */
    public boolean esPar(int valor) {
        return valor % 2 == 0;
    }
}
