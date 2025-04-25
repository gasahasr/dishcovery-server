import Foundation

enum RestaurantError: Error {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case serverError(String)
}

class RestaurantService {
    private let baseURL = "http://127.0.0.1:5000"
    
    func fetchRestaurantInfo(name: String, address: String, location: String) async throws -> DishcoveryResponse {
        guard let url = URL(string: "\(baseURL)/api/restaurant") else {
            throw RestaurantError.invalidURL
        }
        
        let requestBody: [String: String] = [
            "name": name,
            "address": address,
            "location": location
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(requestBody)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw RestaurantError.networkError(NSError(domain: "", code: -1))
            }
            
            guard (200...299).contains(httpResponse.statusCode) else {
                if let errorResponse = try? JSONDecoder().decode([String: String].self, from: data),
                   let errorMessage = errorResponse["error"] {
                    throw RestaurantError.serverError(errorMessage)
                }
                throw RestaurantError.serverError("Server returned status code \(httpResponse.statusCode)")
            }
            
            do {
                let decoder = JSONDecoder()
                return try decoder.decode(DishcoveryResponse.self, from: data)
            } catch {
                throw RestaurantError.decodingError(error)
            }
        } catch let error as RestaurantError {
            throw error
        } catch {
            throw RestaurantError.networkError(error)
        }
    }
    
    func checkHealth() async throws -> Bool {
        guard let url = URL(string: "\(baseURL)/api/health") else {
            throw RestaurantError.invalidURL
        }
        
        do {
            print("\n🏥 Checking server health...")
            let (data, response) = try await URLSession.shared.data(from: url)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                print("❌ Health check failed: Invalid response")
                return false
            }
            
            let healthResponse = try JSONDecoder().decode([String: String].self, from: data)
            let isHealthy = healthResponse["status"] == "healthy"
            print(isHealthy ? "✅ Server is healthy" : "❌ Server is unhealthy")
            return isHealthy
        } catch {
            print("❌ Health Check Error: \(error.localizedDescription)")
            return false
        }
    }
} 