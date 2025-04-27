import Foundation
import FirebaseFirestore
import FirebaseAuth

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
    
    func upsertRestaurantDetails(name: String, location: String, placeId: String, recommendedDishes: String) {
        let trimmedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedLocation = location.trimmingCharacters(in: .whitespacesAndNewlines)
        
        guard !trimmedName.isEmpty else {
            errorMessage = "Restaurant name cannot be empty"
            showError = true
            return
        }
        
        guard !trimmedLocation.isEmpty else {
            errorMessage = "Restaurant location cannot be empty"
            showError = true
            return
        }
        
        let timestamp = Timestamp(date: Date())
        let restaurantData: [String: Any] = [
            "restaurant": trimmedName,
            "location": trimmedLocation,
            "placeId": placeId,
            "recommendedDishes": recommendedDishes,
            "timestamp": timestamp
        ]
        
        // Query for existing restaurant with the same placeId
        db.collection("restaurant_details")
            .whereField("placeId", isEqualTo: placeId)
            .getDocuments { [weak self] snapshot, error in
                if let error = error {
                    self?.errorMessage = "Error checking for existing restaurant details: \(error.localizedDescription)"
                    self?.showError = true
                    return
                }
                
                if let document = snapshot?.documents.first {
                    // Update existing document
                    document.reference.updateData(restaurantData) { error in
                        if let error = error {
                            self?.errorMessage = "Error updating restaurant details: \(error.localizedDescription)"
                            self?.showError = true
                            return
                        }
                        
                        DispatchQueue.main.async {
                            self?.getAllRestaurantDetails()
                        }
                    }
                } else {
                    // Create new document
                    self?.db.collection("restaurant_details").document().setData(restaurantData) { error in
                        if let error = error {
                            self?.errorMessage = "Error saving restaurant details: \(error.localizedDescription)"
                            self?.showError = true
                            return
                        }
                        
                        DispatchQueue.main.async {
                            self?.getAllRestaurantDetails()
                        }
                    }
                }
            }
    }
    
    func getAllRestaurantDetails() {
        db.collection("restaurant_details")
            .order(by: "timestamp", descending: true)
            .addSnapshotListener { [weak self] snapshot, error in
                if let error = error {
                    self?.errorMessage = "Error fetching restaurant details: \(error.localizedDescription)"
                    self?.showError = true
                    return
                }
                
                guard let documents = snapshot?.documents else {
                    self?.searchedRestaurants = []
                    return
                }
                
                self?.searchedRestaurants = documents.compactMap { document in
                    let data = document.data()
                    guard let name = data["restaurant"] as? String,
                          let location = data["location"] as? String,
                          let placeId = data["placeId"] as? String,
                          let recommendedDishes = data["recommendedDishes"] as? String,
                          let timestamp = data["timestamp"] as? Timestamp else {
                        return nil
                    }
                    
                    return Restaurant(
                        id: document.documentID,
                        name: name,
                        userId: "", // Since this is a public collection, we don't need userId
                        placeId: placeId,
                        recommendedDishes: recommendedDishes,
                        location: location,
                        timestamp: timestamp.dateValue()
                    )
                }
            }
    }
    
    func testUpsertOperations() {
        print("Starting upsert operations test...")
        
        // Get the current user's ID
        guard let currentUser = Auth.auth().currentUser else {
            print("Error: No user is currently signed in")
            return
        }
        
        let testUserId = currentUser.uid
        print("Using current user ID: \(testUserId)")
        
        // Test data
        let testName = "Test Restaurant"
        let testLocation = "123 Test Street, Test City"
        let testPlaceId = "test_place_id_\(UUID().uuidString)"
        let testRecommendedDishes = "Test Dish 1, Test Dish 2"
        
        // Test upsertRestaurant
        print("\nTesting upsertRestaurant...")
        upsertRestaurant(
            name: testName,
            userId: testUserId,
            placeId: testPlaceId,
            recommendedDishes: testRecommendedDishes
        )
        
        // Wait for 2 seconds to allow the first operation to complete
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
            // Test upsertRestaurantDetails
            print("\nTesting upsertRestaurantDetails...")
            self?.upsertRestaurantDetails(
                name: testName,
                location: testLocation,
                placeId: testPlaceId,
                recommendedDishes: testRecommendedDishes
            )
            
            // Wait for 2 seconds to allow the second operation to complete
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
                // Verify the data in both collections
                print("\nVerifying data in both collections...")
                
                // Check restaurants_searched collection
                self?.db.collection("restaurants_searched")
                    .whereField("placeId", isEqualTo: testPlaceId)
                    .whereField("userId", isEqualTo: testUserId)
                    .getDocuments { snapshot, error in
                        if let error = error {
                            print("Error checking restaurants_searched: \(error.localizedDescription)")
                            return
                        }
                        
                        if let document = snapshot?.documents.first {
                            print("\nFound in restaurants_searched:")
                            print("Document ID: \(document.documentID)")
                            print("Data: \(document.data())")
                        } else {
                            print("\nNo document found in restaurants_searched")
                        }
                    }
                
                // Check restaurant_details collection
                self?.db.collection("restaurant_details")
                    .whereField("placeId", isEqualTo: testPlaceId)
                    .getDocuments { snapshot, error in
                        if let error = error {
                            print("Error checking restaurant_details: \(error.localizedDescription)")
                            return
                        }
                        
                        if let document = snapshot?.documents.first {
                            print("\nFound in restaurant_details:")
                            print("Document ID: \(document.documentID)")
                            print("Data: \(document.data())")
                        } else {
                            print("\nNo document found in restaurant_details")
                        }
                    }
            }
        }
    }
}

