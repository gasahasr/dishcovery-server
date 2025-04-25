import Foundation
import SwiftUI

@MainActor
class RestaurantViewModel: ObservableObject {
    @Published var recommendedDishes: String = ""
    @Published var placeId: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String = ""
    @Published var showError: Bool = false
    
    private let restaurantService = RestaurantService()
    private let firestoreManager = FirestoreManager()
    
    func fetchRestaurant(name: String, address: String, location: String, userId: String) async {
        isLoading = true
        errorMessage = ""
        showError = false
        
        do {
            let response = try await restaurantService.fetchRestaurantInfo(name: name, address: address, location: location)
            recommendedDishes = response.recommendedDishes
            placeId = response.placeId
            
            // Save to Firebase with upsert operation using the Yelp place ID
            firestoreManager.upsertRestaurant(
                name: name,
                userId: userId,
                placeId: placeId,
                recommendedDishes: recommendedDishes
            )
        } catch let error as RestaurantError {
            errorMessage = error.localizedDescription
            showError = true
        } catch {
            errorMessage = "An unexpected error occurred"
            showError = true
        }
        
        isLoading = false
    }
    
    func formatRating(_ rating: Double?) -> String {
        guard let rating = rating else { return "N/A" }
        return String(format: "%.1f", rating)
    }
    
    func formatDate(_ dateString: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        
        if let date = dateFormatter.date(from: dateString) {
            dateFormatter.dateFormat = "MMM d, yyyy"
            return dateFormatter.string(from: date)
        }
        return dateString
    }
} 
