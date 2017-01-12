import java.io.*;
import java.util.Scanner;

public class QuickSort {
    private static int [] array = new int[2000];

    public static void main(String [] args) {
        readFile();
        
        quickSort(0, array.length - 1);
        
        /*for(int i: array) {
            System.out.print(i + " ");
        }*/
    }
    
    private static void readFile() {
        Scanner scanner = null;

        try {
            scanner = new Scanner(new File("nums"));
        } catch (FileNotFoundException e) {}

        int i = 0;
        while(i < array.length ) {
            array[i] = scanner.nextInt();
            i++;
        }
    }
 
    private static void quickSort(int lowerIndex, int higherIndex) {
         
        int i = lowerIndex;
        int j = higherIndex;
        // calculate pivot number, I am taking pivot as middle index number
        int pivot = array[lowerIndex+(higherIndex-lowerIndex)/2];
        // Divide into two arrays
        while (i <= j) {
            while (array[i] < pivot) {
                i++;
            }
            while (array[j] > pivot) {
                j--;
            }
            if (i <= j) {
                exchangeNumbers(i, j);
                //move index to next position on both sides
                i++;
                j--;
            }
        }
        // call quickSort() method recursively
        if (lowerIndex < j)
            quickSort(lowerIndex, j);
        if (i < higherIndex)
            quickSort(i, higherIndex);
    }
 
    private static void exchangeNumbers(int i, int j) {
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}