import Foundation
import FirebaseFirestore

class FirestoreManager: ObservableObject {
    @Published var restaurant: Restaurant?
    @Published var searchedRestaurants: [Restaurant] = []
    @Published var errorMessage: String = ""
    @Published var showError: Bool = false
    private let db = Firestore.firestore()
    
    func upsertRestaurant(name: String, userId: String, placeId: String, recommendedDishes: String) {
        let trimmedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedName.isEmpty else {
            errorMessage = "Restaurant name cannot be empty"
            showError = true
            return
        }
        
        let timestamp = Timestamp(date: Date())
        let restaurantData: [String: Any] = [
            "restaurant": trimmedName,
            "userId": userId,
            "placeId": placeId,
            "recommendedDishes": recommendedDishes,
            "timestamp": timestamp
        ]
        
        // Query for existing restaurant with the same placeId and userId
        db.collection("restaurants_searched")
            .whereField("placeId", isEqualTo: placeId)
            .whereField("userId", isEqualTo: userId)
            .getDocuments { [weak self] snapshot, error in
                if let error = error {
                    self?.errorMessage = "Error checking for existing restaurant: \(error.localizedDescription)"
                    self?.showError = true
                    return
                }
                
                if let document = snapshot?.documents.first {
                    // Update existing document
                    document.reference.updateData(restaurantData) { error in
                        if let error = error {
                            self?.errorMessage = "Error updating restaurant: \(error.localizedDescription)"
                            self?.showError = true
                            return
                        }
                        
                        DispatchQueue.main.async {
                            self?.restaurant = Restaurant(
                                id: document.documentID,
                                name: trimmedName,
                                userId: userId,
                                placeId: placeId,
                                recommendedDishes: recommendedDishes,
                                timestamp: timestamp.dateValue()
                            )
                            self?.getAllRestaurantsForUser(userId: userId)
                        }
                    }
                } else {
                    // Create new document
                    self?.db.collection("restaurants_searched").document().setData(restaurantData) { error in
                        if let error = error {
                            self?.errorMessage = "Error saving restaurant: \(error.localizedDescription)"
                            self?.showError = true
                            return
                        }
                        
                        DispatchQueue.main.async {
                            self?.restaurant = Restaurant(
                                name: trimmedName,
                                userId: userId,
                                placeId: placeId,
                                recommendedDishes: recommendedDishes,
                                timestamp: timestamp.dateValue()
                            )
                            self?.getAllRestaurantsForUser(userId: userId)
                        }
                    }
                }
            }
    }
    
    func getAllRestaurantsForUser(userId: String) {
        db.collection("restaurants_searched")
            .whereField("userId", isEqualTo: userId)
            .order(by: "timestamp", descending: true)
            .getDocuments { [weak self] snapshot, error in
                if let error = error {
                    self?.errorMessage = "Error getting restaurants: \(error.localizedDescription)"
                    self?.showError = true
                    return
                }
                
                var restaurants: [Restaurant] = []
                
                for document in snapshot?.documents ?? [] {
                    let data = document.data()
                    if let restaurantName = data["restaurant"] as? String,
                       let placeId = data["placeId"] as? String,
                       let recommendedDishes = data["recommendedDishes"] as? String,
                       let timestamp = data["timestamp"] as? Timestamp {
                        let restaurant = Restaurant(
                            id: document.documentID,
                            name: restaurantName,
                            userId: userId,
                            placeId: placeId,
                            recommendedDishes: recommendedDishes,
                            timestamp: timestamp.dateValue()
                        )
                        restaurants.append(restaurant)
                    }
                }
                
                DispatchQueue.main.async {
                    self?.searchedRestaurants = restaurants
                }
            }
    }
} 